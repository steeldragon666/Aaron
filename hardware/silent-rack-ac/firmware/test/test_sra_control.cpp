// Unit tests for sra_control.h.  Build and run on a PC:
//   g++ -std=c++17 -Wall -Wextra -Werror -I../components/sra_control test_sra_control.cpp -o t && ./t
#include "sra_control.h"

#include <cstdio>
#include <cstdlib>
#include <initializer_list>

using namespace sra;

static int g_fail = 0, g_pass = 0;
#define CHECK(cond)                                                       \
  do {                                                                    \
    if (cond) {                                                           \
      g_pass++;                                                           \
    } else {                                                              \
      g_fail++;                                                           \
      std::printf("  FAIL %s:%d  %s\n", __FILE__, __LINE__, #cond);       \
    }                                                                     \
  } while (0)

// A rack at steady temperatures; tests change one thing at a time.
static Inputs rack(float cold, float hot, int8_t cooling = 1) {
  Inputs in;
  in.cold = cold;
  in.hot = hot;
  in.ret = hot - 1.0f;
  in.room = 24.0f;
  in.supply = cooling == 1 ? in.ret - 12.0f : in.ret - 0.5f;
  in.exhaust = cooling == 1 ? 50.0f : 25.0f;
  in.rh_cold = 40.0f;
  return in;
}

// Steps the controller once a second from t0 to t1 with fixed inputs; returns the last output
// and counts the transmissions.
static Outputs run(Controller &c, const Inputs &in, uint32_t t0, uint32_t t1, int *sends = nullptr) {
  Outputs o;
  for (uint32_t t = t0; t <= t1; t++) {
    o = c.step(in, t);
    if (sends && o.send) (*sends)++;
  }
  return o;
}

static void test_start() {
  std::puts("start: sends at once, AC on at target + offset");
  Controller c;
  Outputs o = c.step(rack(22, 33), 0);
  CHECK(o.send);
  CHECK(o.ac_on);
  CHECK(o.setpoint == 25.0f);
  CHECK(o.alarms == 0);
  o = c.step(rack(22, 33), 1);
  CHECK(!o.send);
}

static void test_start_off() {
  std::puts("start in OFF mode: AC off, still sent");
  Controller c;
  c.s.mode = MODE_OFF;
  Outputs o = c.step(rack(22, 33, 0), 0);
  CHECK(o.send);
  CHECK(!o.ac_on);
  CHECK(o.state == ST_OFF);
}

static void test_eco_cycle() {
  std::puts("eco: low load pulls down, switches off after min_on_s, back on when warm after min_off_s");
  Controller c;
  Inputs low = rack(19.0f, 21.0f, 0);   // hot - cold = 2 K: low load; cold average <= 22 - 2
  Outputs o = c.step(low, 0);
  CHECK(o.eco);
  CHECK(o.setpoint == 18.0f);            // eco pull-down: target - band - 2
  o = run(c, low, 1, 899);
  CHECK(o.ac_on);                        // minimum on time
  o = c.step(low, 900);
  CHECK(!o.ac_on);
  CHECK(o.send);                         // the OFF goes out at once
  CHECK(o.state == ST_ECO_OFF);
  // warms up with the AC off (server fans only: hot - cold is larger, the estimate is frozen)
  Inputs warm = rack(24.5f, 31.0f, 0);
  o = run(c, warm, 901, 1199);
  CHECK(!o.ac_on);                       // minimum off time
  CHECK(o.load_dt < 2.5f);
  o = c.step(warm, 1200);
  CHECK(o.ac_on);
  CHECK(o.send);
  CHECK(o.setpoint == 18.0f);
}

static void test_eco_needs_low_load() {
  std::puts("eco: no switch-off at normal load, even with a cool cold side");
  Controller c;
  Outputs o = run(c, rack(19.0f, 31.0f, 1), 0, 5000);   // 12 K rise: about 1.5 kW
  CHECK(o.ac_on);
  CHECK(!o.eco);
}

static void test_eco_leaves_on_load() {
  std::puts("eco: leaves eco when the load rises, back to the trimmed setpoint");
  Controller c;
  run(c, rack(21.0f, 23.0f, 0), 0, 600);
  Outputs o = c.step(rack(21.0f, 23.0f, 0), 601);
  CHECK(o.eco);
  o = run(c, rack(21.0f, 33.0f, 1), 602, 3000);          // 12 K rise now
  CHECK(!o.eco);
  CHECK(o.setpoint >= 25.0f);                             // back on the trim (not the eco 18)
  CHECK(o.ac_on);
}

static void test_eco_disabled() {
  std::puts("eco off: AC stays on at low load");
  Controller c;
  c.s.eco = false;
  Outputs o = run(c, rack(18, 20, 0), 0, 5000);
  CHECK(o.ac_on);
  CHECK(!o.eco);
}

static void test_over_temp_skips_min_off() {
  std::puts("eco off + over-temperature: on at once, fan high");
  Controller c;
  c.s.min_on_s = 0;
  Outputs o = run(c, rack(19, 21, 0), 0, 5);
  CHECK(!o.ac_on);
  o = c.step(rack(27.5f, 38.0f, 0), 6);   // above warn_cold, min_off not met
  CHECK(o.ac_on);
  CHECK(o.fan == FAN_HIGH);
  CHECK(o.alarms & AL_COLD_WARN);
}

static void test_trim() {
  std::puts("trim: setpoint follows the mean cold-side error per window; fast when far off; clamped");
  Controller c;
  c.s.avg_s = 0;                               // raw readings: the steps are easier to follow
  Outputs o = run(c, rack(23.5f, 34.0f), 0, 1199);
  CHECK(o.setpoint == 25.0f);
  o = c.step(rack(23.5f, 34.0f), 1200);
  CHECK(o.setpoint == 24.0f);
  CHECK(o.send);
  o = run(c, rack(22.8f, 34.0f), 1201, 4000);  // inside the 1 K band: no change
  CHECK(o.setpoint == 24.0f);
  // too cold: up 1 per window (the first window still holds 400 s of the old level)
  o = run(c, rack(20.5f, 30.0f), 4001, 4001 + 3 * 1200);
  CHECK(o.setpoint == 26.0f);
  o = run(c, rack(26.0f, 38.0f), 8000, 8000 + 120 * 10);   // 4 K over: fast, 2 K steps
  CHECK(o.setpoint == 17.0f);                  // clamped at sp_min
  c.s.eco = false;                             // (eco would switch it off down here)
  o = run(c, rack(15.0f, 20.0f), 10000, 10000 + 1200 * 20);
  CHECK(o.setpoint == 30.0f);                  // clamped at sp_max
}

static void test_trim_ignores_cycling() {
  std::puts("trim: a cold side swinging +-4 K with the compressor does not move the setpoint");
  for (uint32_t cycle : {600u, 840u, 1200u}) {        // compressor cycles of 10, 14 and 20 min
    Controller c;
    Outputs o;
    float sp_1h = 0.0f;
    for (uint32_t t = 0; t < 6 * 3600; t++) {
      float cold = ((t / (cycle / 2)) % 2) ? 26.0f : 18.0f;
      o = c.step(rack(cold, cold + 11.0f, 1), t);
      if (t == 3600) sp_1h = o.setpoint;
      if (t >= 3600 && std::fabs(o.cold_avg - 22.0f) >= 2.5f) CHECK(false);
    }
    CHECK(std::fabs(sp_1h - 25.0f) <= 1.0f);         // at most one step while the average settles
    CHECK(o.setpoint == sp_1h);                      // then it stays put
  }
}

static void test_not_cooling() {
  std::puts("not cooling: re-send after verify, alarm after the retries, clears when cooling");
  Controller c;
  c.s.trim_s = 100000;                         // keep the trim out of this test
  Inputs stuck = rack(24.0f, 36.0f, 0);       // ret 35 > sp + 1.5, compressor not running
  int sends = 0;
  Outputs o = run(c, stuck, 0, 899, &sends);
  CHECK(sends == 1);                           // the start only
  CHECK(o.retries == 0);
  o = run(c, stuck, 900, 900, &sends);
  CHECK(o.send);
  CHECK(o.retries == 1);
  o = run(c, stuck, 901, 900 * 4 - 1, &sends);
  CHECK(o.retries == 3);
  CHECK(!(o.alarms & AL_NOT_COOLING));
  o = c.step(stuck, 900 * 4);                  // the fourth miss raises the alarm
  CHECK(o.alarms & AL_NOT_COOLING);
  CHECK(o.send);                               // and it keeps trying
  o = run(c, stuck, 900 * 4 + 1, 900 * 5, &sends);
  CHECK(o.alarms & AL_NOT_COOLING);
  CHECK(o.state == ST_NOT_COOLING);
  o = run(c, rack(23.0f, 34.0f, 1), 900 * 5 + 1, 900 * 5 + 5);
  CHECK(!(o.alarms & AL_NOT_COOLING));
  CHECK(o.retries == 0);
  CHECK(o.state == ST_COOLING);
}

static void test_not_cooling_hot_is_faster() {
  std::puts("not cooling while hot: re-send after verify_hot_s");
  Controller c;
  Inputs hot = rack(26.0f, 38.0f, 0);         // 4 K over target
  int sends = 0;
  Outputs o = run(c, hot, 0, 179, &sends);
  CHECK(o.retries == 0);
  o = run(c, hot, 180, 180, &sends);
  CHECK(o.retries == 1);
}

static void test_thermostat_satisfied_is_not_a_fault() {
  std::puts("compressor resting with return below setpoint + 1.5: no retries");
  Controller c;
  Inputs rest = rack(21.5f, 26.0f, 0);        // ret 25 < 25 + 1.5, normal load
  Outputs o = run(c, rest, 0, 4000);
  CHECK(o.retries == 0);
  CHECK(o.state == ST_IDLE);
}

static void test_unknown_cooling() {
  std::puts("no supply/exhaust probes: cooling unknown, no false alarms");
  Controller c;
  Inputs in = rack(24, 36, 0);
  in.supply = NAN;
  in.exhaust = NAN;
  Outputs o = run(c, in, 0, 5000);
  CHECK(o.cooling == -1);
  CHECK(o.retries == 0);
  CHECK(o.state == ST_ON);
}

static void test_user_off_and_override() {
  std::puts("user OFF: stays off, overridden when the cold side passes warn + 2");
  Controller c;
  c.s.mode = MODE_OFF;
  Outputs o = run(c, rack(26, 36, 0), 0, 100);
  CHECK(!o.ac_on);
  o = c.step(rack(29.5f, 40.0f, 0), 101);
  CHECK(o.ac_on);
  CHECK(o.alarms & AL_OVERRIDE);
  o = c.step(rack(24.0f, 35.0f, 1), 102);
  CHECK(!o.ac_on);                             // cooled down: back to the user's OFF
}

static void test_mode_on() {
  std::puts("mode ON: never eco-off");
  Controller c;
  c.s.mode = MODE_ON;
  c.s.min_on_s = 0;
  Outputs o = run(c, rack(15, 17, 0), 0, 3000);
  CHECK(o.ac_on);
}

static void test_sensor_fail_safe() {
  std::puts("cold side lost: AC forced on, sensor alarm, setpoint back to the safe guess");
  Controller c;
  c.s.min_on_s = 0;
  Outputs o = run(c, rack(19, 21, 0), 0, 5);
  CHECK(!o.ac_on);
  Inputs blind = rack(19, 21, 0);
  blind.cold = NAN;
  o = c.step(blind, 6);
  CHECK(o.ac_on);
  CHECK(o.alarms & AL_SENSOR);
  Inputs no_hot = rack(19, 21, 0);
  no_hot.hot = NAN;
  no_hot.ret = NAN;
  o = run(c, no_hot, 7, 3000);
  CHECK(o.ac_on);                              // no eco without the hot side
  CHECK(o.alarms & AL_SENSOR);
}

static void test_critical_shutdown() {
  std::puts("critical: shutdown request after crit_delay_s, latched until 3 K under");
  Controller c;
  c.s.crit_delay_s = 300;
  Outputs o = run(c, rack(33, 45, 0), 0, 299);
  CHECK(o.alarms & AL_COLD_CRIT);
  CHECK(!o.shutdown);
  CHECK(o.state == ST_CRITICAL);
  o = c.step(rack(33, 45, 0), 300);
  CHECK(o.shutdown);
  CHECK(o.alarms & AL_SHUTDOWN);
  o = run(c, rack(30, 40, 1), 301, 400);
  CHECK(o.shutdown);                           // 30 > 32 - 3
  o = c.step(rack(28.5f, 38, 1), 401);
  CHECK(!o.shutdown);
}

static void test_door_and_leak() {
  std::puts("door alarm after door_alarm_s; leak alarm at once");
  Controller c;
  Inputs in = rack(22, 33);
  in.door_open = true;
  Outputs o = run(c, in, 0, 599);
  CHECK(!(o.alarms & AL_DOOR));
  o = c.step(in, 600);
  CHECK(o.alarms & AL_DOOR);
  in.door_open = false;
  in.leak = true;
  o = c.step(in, 601);
  CHECK(!(o.alarms & AL_DOOR));
  CHECK(o.alarms & AL_LEAK);
}

static void test_condensation() {
  std::puts("condensation: dew point 1 K over the supply air for 10 minutes");
  Controller c;
  Inputs in = rack(22, 33);                    // supply 20 degC
  in.rh_cold = 95.0f;                          // dew point about 21.2 degC
  Outputs o = run(c, in, 0, 599);
  CHECK(!(o.alarms & AL_CONDENSATION));
  o = c.step(in, 600);
  CHECK(o.alarms & AL_CONDENSATION);
  CHECK(o.dew_point > 21.0f && o.dew_point < 21.4f);
  in.rh_cold = 40.0f;
  o = c.step(in, 601);
  CHECK(!(o.alarms & AL_CONDENSATION));
}

static void test_mains() {
  std::puts("mains: no sends while dead, one re-send mains_delay_s after it returns");
  Controller c;
  int sends = 0;
  Outputs o = run(c, rack(22, 33), 0, 100, &sends);
  CHECK(sends == 1);
  Inputs dead = rack(23, 34, 0);               // warm enough that the trim queues a send
  dead.mains = false;
  o = run(c, dead, 101, 2000, &sends);
  CHECK(sends == 1);
  CHECK(o.alarms & AL_NO_POWER);
  CHECK(o.state == ST_NO_POWER);
  Inputs back = rack(24, 35, 0);
  o = run(c, back, 2001, 2030, &sends);
  CHECK(sends == 1);
  o = run(c, back, 2031, 2031, &sends);
  CHECK(o.send);
  CHECK(sends == 2);
}

static void test_send_rate_limit() {
  std::puts("sends are at least min_send_gap_s apart");
  Controller c;
  c.step(rack(22, 33), 0);
  c.request_send();
  Outputs o = c.step(rack(22, 33), 3);
  CHECK(!o.send);
  o = c.step(rack(22, 33), 10);
  CHECK(o.send);
}

static void test_remote_override_resend_off() {
  std::puts("AC switched on by the handheld remote while eco wants it off: OFF re-sent twice");
  Controller c;
  c.s.min_on_s = 0;
  run(c, rack(19, 21, 0), 0, 20);
  int sends = 0;
  Inputs running = rack(18.5f, 21.0f, 1);      // still cool enough to stay in eco off
  Outputs o = run(c, running, 21, 21 + 900 * 3, &sends);
  CHECK(!o.ac_on);
  CHECK(sends == 2);
}

static void test_reset_alarms() {
  std::puts("reset_alarms clears the latched alarms");
  Controller c;
  run(c, rack(33, 45, 0), 0, 400);
  c.reset_alarms();
  Outputs o = c.step(rack(33, 45, 0), 401);
  CHECK(!o.shutdown);                          // relatches after crit_delay_s again
  CHECK(o.retries == 0);
}

static void test_dew_point() {
  std::puts("dew point formula");
  CHECK(std::fabs(dew_point_c(25.0f, 50.0f) - 13.85f) < 0.1f);
  CHECK(std::fabs(dew_point_c(20.0f, 100.0f) - 20.0f) < 0.05f);
  CHECK(std::isnan(dew_point_c(NAN, 50.0f)));
}

// ---------------------------------------------------------------- office air
static Inputs office_rack(float cold, float hot, float office, int8_t cooling = 1) {
  Inputs in = rack(cold, hot, cooling);
  in.office = office;
  in.office_rpm = 1500.0f;
  return in;
}

static void test_office_off_by_default() {
  std::puts("office: off by default - no fan, the rack's own target");
  Controller c;
  Outputs o = run(c, office_rack(22, 33, 30), 0, 600);
  CHECK(o.office_state == OF_OFF);
  CHECK(o.office_pct == 0);
  CHECK(o.target == 22.0f);
}

static void test_office_auto() {
  std::puts("office: auto - colder target at once, fan after its rest, stops when satisfied, setpoint restored");
  Controller c;
  c.s.office_mode = OFFICE_AUTO;
  c.s.avg_s = 0;
  Outputs o = c.step(office_rack(22, 33, 26), 0);
  CHECK(o.office_state == OF_WAIT);          // the fan rests after boot
  CHECK(o.office_pct == 0);
  CHECK(o.target == 18.0f);                  // cold side pulled down for the office
  CHECK(o.setpoint == 21.0f);                // first guess: office supply + offset
  o = run(c, office_rack(22, 33, 26), 1, 119);
  CHECK(o.office_pct == 0);
  o = c.step(office_rack(22, 33, 26), 120);
  CHECK(o.office_state == OF_COOLING);
  CHECK(o.office_pct == 100);                // 2.5 K over the stop point: full speed
  o = run(c, office_rack(22, 33, 24.0f), 121, 200);
  CHECK(o.office_pct >= 45 && o.office_pct <= 50);   // 0.5 K over the stop point: 30 + 70 x 0.25
  o = c.step(office_rack(22, 33, 23.4f), 201);
  CHECK(o.office_pct == 0);                  // satisfied: stops at once
  CHECK(o.office_state == OF_IDLE);
  CHECK(o.target == 22.0f);
  CHECK(o.setpoint >= 25.0f);                // the rack's own setpoint is back
}

static void test_office_rack_first() {
  std::puts("office: rack first - a warm cold side or an alarm blocks it, the fan stops at once");
  Controller c;
  c.s.office_mode = OFFICE_AUTO;
  c.s.avg_s = 0;
  Outputs o = run(c, office_rack(24.0f, 35, 27), 0, 300);    // cold side 2 K over its target
  CHECK(o.office_state == OF_BLOCKED);
  CHECK(o.office_pct == 0);
  CHECK(o.target == 22.0f);
  o = run(c, office_rack(22.8f, 34, 27), 301, 400);          // 0.8 K over: still blocked (hysteresis)
  CHECK(o.office_state == OF_BLOCKED);
  o = run(c, office_rack(22.4f, 33, 27), 401, 600);          // released at 0.5 K over
  CHECK(o.office_state == OF_COOLING);
  CHECK(o.office_pct > 0);
  Inputs wet = office_rack(22.4f, 33, 27);
  wet.leak = true;
  o = c.step(wet, 601);
  CHECK(o.office_state == OF_BLOCKED);
  CHECK(o.office_pct == 0);                                  // at once, no minimum run
}

static void test_office_holds_off_eco() {
  std::puts("office: a call holds eco off and brings the AC back after its rest");
  Controller c;
  c.s.office_mode = OFFICE_AUTO;
  Inputs low = office_rack(19.0f, 21.0f, 23.0f, 0);          // low load, office satisfied
  Outputs o = run(c, low, 0, 900);
  CHECK(!o.ac_on);                                           // eco switched it off at min_on_s
  CHECK(o.office_state == OF_IDLE);
  Inputs call = office_rack(19.0f, 21.0f, 25.0f, 0);
  o = run(c, call, 901, 1199);
  CHECK(!o.ac_on);                                           // the compressor rests first
  CHECK(!o.eco);
  CHECK(o.office_state == OF_COOLING);                       // the plenum is still cold: the fan runs meanwhile
  o = c.step(call, 1200);
  CHECK(o.ac_on);
  CHECK(o.send);
}

static void test_office_waits_for_cold_air() {
  std::puts("office: no fan until the cold side is clearly colder than the office");
  Controller c;
  c.s.office_mode = OFFICE_AUTO;
  c.s.avg_s = 0;
  Outputs o = run(c, office_rack(23.4f, 34, 24.6f), 0, 300); // calls, but only 1.2 K colder
  CHECK(o.office_state == OF_WAIT);
  CHECK(o.office_pct == 0);
  CHECK(o.target == 18.0f);                                  // the rack is pulled down meanwhile
  o = run(c, office_rack(22.0f, 33, 24.6f), 301, 400);
  CHECK(o.office_state == OF_COOLING);
}

static void test_office_on_and_no_probe() {
  std::puts("office: ON runs the fan at its maximum without a probe; AUTO without a probe does nothing");
  Controller c;
  c.s.office_mode = OFFICE_ON;
  c.s.office_fan_max = 80;
  Outputs o = run(c, rack(22, 33), 0, 200);                  // no office probe
  CHECK(o.office_state == OF_COOLING);
  CHECK(o.office_pct == 80);
  c.s.office_mode = OFFICE_AUTO;
  o = c.step(rack(22, 33), 201);
  CHECK(o.office_state == OF_NO_PROBE);
  CHECK(o.office_pct == 0);
  CHECK(o.target == 22.0f);
}

static void test_office_fan_alarm() {
  std::puts("office: a fan told to run that does not turn raises AL_OFFICE_FAN after a minute");
  Controller c;
  c.s.office_mode = OFFICE_AUTO;
  c.s.avg_s = 0;
  Inputs in = office_rack(22, 33, 26);
  in.office_rpm = 0.0f;
  Outputs o = run(c, in, 0, 179);                            // the fan is told to run from 120 s
  CHECK(!(o.alarms & AL_OFFICE_FAN));
  o = c.step(in, 180);
  CHECK(o.alarms & AL_OFFICE_FAN);
  in.office_rpm = 1500.0f;
  o = c.step(in, 181);
  CHECK(!(o.alarms & AL_OFFICE_FAN));
}

static void test_office_dew_point_floor() {
  std::puts("office: the colder target stays 2 K over the room dew point (a dry office grille)");
  Controller c;
  c.s.office_mode = OFFICE_AUTO;
  Inputs in = office_rack(22, 33, 26);
  in.room = 26.0f;
  in.rh_room = 60.0f;                                        // dew point 17.6
  Outputs o = c.step(in, 0);
  CHECK(std::fabs(o.target - 19.6f) < 0.1f);
  in.rh_room = 80.0f;                                        // dew point 22.3: no lower than the rack's target
  o = c.step(in, 1);
  CHECK(o.target == 22.0f);
}

static void test_office_user_off_blocks() {
  std::puts("office: the user's AC OFF blocks office air");
  Controller c;
  c.s.office_mode = OFFICE_AUTO;
  c.s.mode = MODE_OFF;
  Outputs o = run(c, office_rack(22, 33, 26, 0), 0, 300);
  CHECK(o.office_state == OF_BLOCKED);
  CHECK(o.office_pct == 0);
  CHECK(!o.ac_on);
}

static void test_office_min_run() {
  std::puts("office: once running, the fan keeps going for office_min_s when the cold air runs out");
  Controller c;
  c.s.office_mode = OFFICE_AUTO;
  c.s.avg_s = 0;
  Outputs o = run(c, office_rack(21, 33, 26), 0, 120);       // starts at 120
  CHECK(o.office_pct > 0);
  o = run(c, office_rack(23.4f, 33, 24.0f), 121, 239);       // only 0.6 K colder now: not useful
  CHECK(o.office_pct > 0);                                   // still inside the minimum run
  o = c.step(office_rack(23.4f, 33, 24.0f), 240);
  CHECK(o.office_pct == 0);
  CHECK(o.office_state == OF_WAIT);
}

int main() {
  test_start();
  test_start_off();
  test_eco_cycle();
  test_eco_needs_low_load();
  test_eco_leaves_on_load();
  test_eco_disabled();
  test_over_temp_skips_min_off();
  test_trim();
  test_trim_ignores_cycling();
  test_not_cooling();
  test_not_cooling_hot_is_faster();
  test_thermostat_satisfied_is_not_a_fault();
  test_unknown_cooling();
  test_user_off_and_override();
  test_mode_on();
  test_sensor_fail_safe();
  test_critical_shutdown();
  test_door_and_leak();
  test_condensation();
  test_mains();
  test_send_rate_limit();
  test_remote_override_resend_off();
  test_reset_alarms();
  test_dew_point();
  test_office_off_by_default();
  test_office_auto();
  test_office_rack_first();
  test_office_holds_off_eco();
  test_office_waits_for_cold_air();
  test_office_on_and_no_probe();
  test_office_fan_alarm();
  test_office_dew_point_floor();
  test_office_user_off_blocks();
  test_office_min_run();
  std::printf("%d checks passed, %d failed\n", g_pass, g_fail);
  return g_fail ? EXIT_FAILURE : EXIT_SUCCESS;
}
