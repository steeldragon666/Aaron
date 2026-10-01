// sra_control.h - SRA-16 rack cooling supervisor (CP-SRA16-ELC-001).
//
// Pure logic with no ESPHome or Arduino dependencies: the same file is unit-tested on a PC
// (firmware/test/test_sra_control.cpp), driven by a thermal model of the rack
// (tools/sim_controller.py) and compiled into the rack node firmware (firmware/sra16-node.yaml).
//
// The AC keeps its own thermostat, which cycles the compressor on the AC's return air.  This code
// supervises it through the AC's IR remote protocol:
//   - normal load: AC on, setpoint trimmed so the server intake (cold side) averages the target;
//   - low IT load (eco): pull the rack down, switch the AC off, switch it back on when it warms
//     up - long quiet off periods, compressor-friendly minimum on and off times;
//   - notices when the AC is not cooling (power cut, missed IR) and re-sends the state;
//   - raises alarms and, if the cold side stays critical, asks for the IT to shut down.
// Decisions use smoothed temperatures: a cycling compressor swings the cold side by several
// kelvin.  Alarms use the raw readings.
// Fail-safe rule: anything unknown (no cold or hot reading, over-temperature) means "AC on".
#pragma once

#include <cmath>
#include <cstdint>

namespace sra {

enum Mode : uint8_t { MODE_AUTO = 0, MODE_ON = 1, MODE_OFF = 2 };
enum Fan : uint8_t { FAN_AUTO = 0, FAN_LOW = 1, FAN_HIGH = 2 };
enum State : uint8_t {
  ST_STARTING = 0,     // just switched on, waiting for the coil to cool
  ST_COOLING = 1,      // compressor running
  ST_IDLE = 2,         // AC on, its thermostat satisfied (compressor resting)
  ST_ON = 3,           // AC on, compressor state unknown (no supply/exhaust probe)
  ST_ECO_OFF = 4,      // switched off by eco (low load)
  ST_OFF = 5,          // switched off by the user
  ST_NOT_COOLING = 6,  // should be cooling but is not, after the retries
  ST_NO_POWER = 7,     // mains-detect input says the AC socket is dead
  ST_CRITICAL = 8,     // cold side above the critical limit
};

enum Alarm : uint16_t {
  AL_COLD_WARN = 1u << 0,     // cold side above warn_cold
  AL_COLD_CRIT = 1u << 1,     // cold side above crit_cold
  AL_HOT_WARN = 1u << 2,      // hot side above warn_hot
  AL_NOT_COOLING = 1u << 3,   // asked to cool, still not cooling after max_retries
  AL_LEAK = 1u << 4,          // water in the drip tray
  AL_DOOR = 1u << 5,          // a door open for longer than door_alarm_s
  AL_SENSOR = 1u << 6,        // no working probe on the cold or the hot side
  AL_CONDENSATION = 1u << 7,  // cold-side dew point 1 K above the supply air for 10 minutes
  AL_OVERRIDE = 1u << 8,      // user OFF overridden because it got too hot
  AL_SHUTDOWN = 1u << 9,      // IT shutdown requested
  AL_NO_POWER = 1u << 10,     // AC socket dead (mains-detect input)
  AL_LINK = 1u << 11,         // reserved: set by the touchscreen when the node stops answering
};

struct Settings {
  uint8_t mode = MODE_AUTO;
  uint8_t fan = FAN_AUTO;
  bool eco = true;              // allow switching the AC off at low load
  float target = 22.0f;         // server intake (cold side) target, degC (average)
  float warn_cold = 27.0f;      // ASHRAE A1 recommended maximum intake
  float crit_cold = 32.0f;      // shutdown request after crit_delay_s above this
  float warn_hot = 45.0f;
  float eco_dt = 4.0f;          // low load: hot - cold below this (about 500 W at the AC's air flow)
  float eco_band = 2.0f;        // eco: off at target - band (average), back on at target + band
  float eco_hot_on = 32.0f;     //   or when the hot side passes this
  uint32_t min_on_s = 900;      // compressor-friendly minimum on and off times
  uint32_t min_off_s = 300;
  float sp_min = 17.0f;         // AC setpoint range (whole degrees are sent)
  float sp_max = 30.0f;
  float sp_offset = 3.0f;       // first guess: AC setpoint = target + offset
  uint32_t avg_s = 600;         // time constant of the averages used for decisions
  uint32_t trim_s = 1200;       // setpoint trim: on the mean error over this window
  uint32_t trim_fast_s = 120;   // ... every this when the cold side averages 3 K over target
  float trim_band = 1.0f;       // the AC takes whole degrees
  uint32_t verify_s = 900;      // on, should be cooling, is not: re-send after this
  uint32_t verify_hot_s = 180;  // ... or this, when the cold side is 3 K over target
  uint8_t max_retries = 3;
  uint32_t door_alarm_s = 600;
  uint32_t crit_delay_s = 120;  // the rack heats about 1 K/min with the AC down at full load
  uint32_t mains_delay_s = 30;  // re-send this long after the AC socket comes back
  uint32_t min_send_gap_s = 10; // never transmit more often than this
};

struct Inputs {
  float cold = NAN;      // server intake: mean of the cold-side probes
  float hot = NAN;       // server exhaust: highest hot-side probe
  float supply = NAN;    // AC supply air (hood outlet)
  float ret = NAN;       // AC return air (rear plenum, over the return opening); hot is used when missing
  float exhaust = NAN;   // condenser exhaust (elbow)
  float room = NAN;      // room ambient
  float rh_cold = NAN;   // cold-side relative humidity, %
  bool door_open = false;
  bool leak = false;
  bool mains = true;     // AC socket live; leave true when the input is not fitted
};

struct Outputs {
  bool ac_on = true;
  float setpoint = 25.0f;
  uint8_t fan = FAN_AUTO;
  bool send = false;     // transmit the IR state now
  uint8_t state = ST_STARTING;
  uint16_t alarms = 0;
  bool shutdown = false; // latched until the cold side is 3 K below crit_cold
  int8_t cooling = -1;   // inferred compressor state: 1 running, 0 not, -1 unknown
  bool eco = false;      // low load: eco cycling active
  uint8_t retries = 0;
  float dew_point = NAN;
  float cold_avg = NAN;  // averaged server intake
  float load_dt = NAN;   // averaged hot - cold while the AC runs (a load estimate)
};

inline float dew_point_c(float t, float rh) {
  // Magnus formula, good to about 0.4 K for 0-60 degC
  if (std::isnan(t) || std::isnan(rh) || rh <= 0.0f) return NAN;
  const float a = 17.62f, b = 243.12f;
  float g = std::log(rh / 100.0f) + a * t / (b + t);
  return b * g / (a - g);
}

class Controller {
 public:
  Settings s;

  // Set when the touchscreen asks for "send now" or after a settings change.
  void request_send() { want_send_ = true; }
  // Clears the latched alarms (not cooling, shutdown request) and the retry count.
  void reset_alarms() {
    not_cooling_ = false;
    retries_ = 0;
    shutdown_ = false;
    crit_ = false;      // the critical timer starts again
  }

  Outputs step(const Inputs &in, uint32_t now) {
    Outputs o;
    if (!started_) {
      started_ = true;
      on_ = s.mode != MODE_OFF;
      sp_trim_ = clamp_sp(std::round(s.target + s.sp_offset));
      t_switch_ = t_trim_ = t_verify_ = t_off_check_ = t_last_ = now;
      want_send_ = true;
      last_fan_ = s.fan;
      last_sp_ = sp_trim_;
      last_mains_ = in.mains;
    }
    const uint32_t dt = now - t_last_;
    t_last_ = now;
    const float cold = in.cold, hot = in.hot;
    const float ret = std::isnan(in.ret) ? hot : in.ret;
    const bool cold_ok = !std::isnan(cold), hot_ok = !std::isnan(hot);
    uint16_t al = 0;
    if (!cold_ok || !hot_ok) al |= AL_SENSOR;

    // ---- averages for decisions
    if (cold_ok) cold_avg_ = std::isnan(cold_avg_) ? cold : ema(cold_avg_, cold, dt);
    // the load estimate only means something while the AC fan moves the loop air
    if (on_ && in.mains && cold_ok && hot_ok)
      load_dt_ = std::isnan(load_dt_) ? hot - cold : ema(load_dt_, hot - cold, dt);

    // ---- compressor running? (supply well below return, or a hot condenser exhaust)
    int8_t cooling = -1;
    if (!std::isnan(in.supply) && !std::isnan(ret)) cooling = (ret - in.supply >= 4.0f) ? 1 : 0;
    if (!std::isnan(in.exhaust) && !std::isnan(in.room)) {
      bool hot_exhaust = in.exhaust - in.room >= 8.0f;
      cooling = (cooling == 1 || hot_exhaust) ? 1 : 0;
    }

    // ---- humidity: in a closed loop the coil dries the air, so its dew point sits just under the
    // supply temperature. Room air let in through an open door lifts it above: then the hood and
    // the plenum, which run at supply temperature, sweat. Flag that once it has lasted 10 minutes.
    o.dew_point = dew_point_c(cold, in.rh_cold);
    if (!std::isnan(o.dew_point) && !std::isnan(in.supply) && o.dew_point >= in.supply + 1.0f) {
      if (!damp_) {
        damp_ = true;
        t_damp_ = now;
      }
      if (now - t_damp_ >= 600) al |= AL_CONDENSATION;
    } else {
      damp_ = false;
    }

    // ---- temperature, leak and door alarms (raw readings)
    if (cold_ok && cold >= s.warn_cold) al |= AL_COLD_WARN;
    if (cold_ok && cold >= s.crit_cold) al |= AL_COLD_CRIT;
    if (hot_ok && hot >= s.warn_hot) al |= AL_HOT_WARN;
    if (in.leak) al |= AL_LEAK;
    if (in.door_open) {
      if (!door_open_) {
        door_open_ = true;
        t_door_ = now;
      }
      if (now - t_door_ >= s.door_alarm_s) al |= AL_DOOR;
    } else {
      door_open_ = false;
    }

    // ---- critical: ask the IT to shut down (latched)
    if (cold_ok && cold >= s.crit_cold) {
      if (!crit_) {
        crit_ = true;
        t_crit_ = now;
      }
      if (now - t_crit_ >= s.crit_delay_s) shutdown_ = true;
    } else {
      crit_ = false;
      if (shutdown_ && cold_ok && cold < s.crit_cold - 3.0f) shutdown_ = false;
    }

    // ---- AC socket power (optional mains-detect input)
    if (in.mains && !last_mains_) {
      mains_back_ = true;
      t_mains_ = now;
    }
    last_mains_ = in.mains;
    if (!in.mains) al |= AL_NO_POWER;
    if (mains_back_ && now - t_mains_ >= s.mains_delay_s) {
      mains_back_ = false;
      want_send_ = true;      // the AC came back with its power, probably in standby
      t_verify_ = now;
      retries_ = 0;
    }

    // ---- on or off?
    const bool too_hot = (cold_ok && cold >= s.warn_cold) || (hot_ok && hot >= s.warn_hot);
    const bool low_load = !std::isnan(load_dt_) && load_dt_ < s.eco_dt + (eco_ ? 1.0f : 0.0f);
    eco_ = s.mode == MODE_AUTO && s.eco && cold_ok && hot_ok && !too_hot && low_load;
    bool want_on = on_;
    if (s.mode == MODE_OFF) {
      want_on = false;
      if ((cold_ok && cold >= s.warn_cold + 2.0f) || (hot_ok && hot >= s.warn_hot + 5.0f)) {
        want_on = true;
        al |= AL_OVERRIDE;
      }
    } else if (s.mode == MODE_ON || !s.eco || !cold_ok || !hot_ok || too_hot) {
      want_on = true;
    } else if (on_) {
      // pulled down far enough at low load: switch off
      if (eco_ && cold_avg_ <= s.target - s.eco_band && now - t_switch_ >= s.min_on_s) want_on = false;
    } else {
      // eco off: back on when it warms up
      bool warm = cold >= s.target + s.eco_band || hot >= s.eco_hot_on;
      if (warm && now - t_switch_ >= s.min_off_s) want_on = true;
    }
    if (want_on != on_) {
      on_ = want_on;
      t_switch_ = t_verify_ = t_off_check_ = t_trim_ = now;
      retries_ = 0;
      off_resends_ = 0;
      not_cooling_ = false;
      want_send_ = true;
    }

    // ---- setpoint: eco pulls down hard; otherwise trim the AC's own thermostat so the cold side
    // averages the target.  The trim acts on the mean error over its whole window, which a
    // cycling compressor cannot alias.
    if (on_ && cold_ok && !eco_) {
      float e = cold_avg_ - s.target;
      err_sum_ += e * (float) dt;
      err_t_ += dt;
      bool fast = e > 3.0f;
      if (now - t_trim_ >= (fast ? s.trim_fast_s : s.trim_s)) {
        float me = fast ? e : (err_t_ > 0 ? err_sum_ / (float) err_t_ : e);
        if (me > s.trim_band) sp_trim_ = clamp_sp(sp_trim_ - (fast ? 2.0f : 1.0f));
        else if (me < -s.trim_band) sp_trim_ = clamp_sp(sp_trim_ + 1.0f);
        t_trim_ = now;
        err_sum_ = 0.0f;
        err_t_ = 0;
      }
    } else {
      t_trim_ = now;
      err_sum_ = 0.0f;
      err_t_ = 0;
    }
    if (!cold_ok && sp_trim_ > s.target + s.sp_offset)
      sp_trim_ = clamp_sp(std::round(s.target + s.sp_offset));   // blind: back to the safe first guess
    const float sp = eco_ ? clamp_sp(s.target - s.eco_band - 2.0f) : sp_trim_;
    if (sp != last_sp_) {
      last_sp_ = sp;
      if (on_) want_send_ = true;
    }

    // ---- fan
    uint8_t fan = too_hot ? (uint8_t) FAN_HIGH : s.fan;
    if (fan != last_fan_) {
      last_fan_ = fan;
      if (on_) want_send_ = true;
    }

    // ---- is the AC doing what it was told?
    const bool should_cool = on_ && in.mains && cooling == 0 && !std::isnan(ret) && ret > sp + 1.5f;
    if (should_cool) {
      // after the alarm, keep trying but at the slow rate (each frame makes the AC beep)
      uint32_t lim = (cold_ok && cold > s.target + 3.0f && !not_cooling_) ? s.verify_hot_s : s.verify_s;
      if (now - t_verify_ >= lim) {
        t_verify_ = now;
        if (retries_ < s.max_retries) retries_++;
        else not_cooling_ = true;
        want_send_ = true;
      }
    } else {
      t_verify_ = now;
      if (cooling == 1 || !on_) {
        retries_ = 0;
        not_cooling_ = false;
      }
    }
    if (not_cooling_) al |= AL_NOT_COOLING;
    // someone switched it on with the handheld remote while we want it off: say OFF again
    if (!on_ && cooling == 1) {
      if (now - t_off_check_ >= 900 && off_resends_ < 2) {
        off_resends_++;
        t_off_check_ = now;
        want_send_ = true;
      }
    } else {
      t_off_check_ = now;
    }

    // ---- transmit (rate-limited; the first one goes at once; nothing while the AC socket is
    // dead or the AC is still booting after its power came back)
    if (want_send_ && in.mains && !mains_back_ && (!sent_once_ || now - t_sent_ >= s.min_send_gap_s)) {
      o.send = true;
      want_send_ = false;
      sent_once_ = true;
      t_sent_ = now;
    }

    if (shutdown_) al |= AL_SHUTDOWN;
    o.ac_on = on_;
    o.setpoint = sp;
    o.fan = fan;
    o.alarms = al;
    o.shutdown = shutdown_;
    o.cooling = cooling;
    o.eco = eco_;
    o.retries = retries_;
    o.cold_avg = cold_avg_;
    o.load_dt = load_dt_;
    if (al & AL_COLD_CRIT) o.state = ST_CRITICAL;
    else if (!in.mains) o.state = ST_NO_POWER;
    else if (not_cooling_) o.state = ST_NOT_COOLING;
    else if (!on_) o.state = s.mode == MODE_OFF ? ST_OFF : ST_ECO_OFF;
    else if (now - t_switch_ < 120 && cooling != 1) o.state = ST_STARTING;
    else if (cooling == 1) o.state = ST_COOLING;
    else if (cooling == 0) o.state = ST_IDLE;
    else o.state = ST_ON;
    return o;
  }

 private:
  float clamp_sp(float v) const { return v < s.sp_min ? s.sp_min : (v > s.sp_max ? s.sp_max : v); }
  float ema(float avg, float x, uint32_t dt) const {
    if (s.avg_s == 0) return x;
    float a = 1.0f - std::exp(-(float) dt / (float) s.avg_s);
    return avg + a * (x - avg);
  }

  bool started_ = false, on_ = true, want_send_ = false, sent_once_ = false, eco_ = false;
  bool door_open_ = false, crit_ = false, shutdown_ = false, damp_ = false;
  bool not_cooling_ = false, last_mains_ = true, mains_back_ = false;
  float sp_trim_ = 25.0f, last_sp_ = 25.0f, cold_avg_ = NAN, load_dt_ = NAN, err_sum_ = 0.0f;
  uint32_t err_t_ = 0;
  uint8_t retries_ = 0, off_resends_ = 0, last_fan_ = FAN_AUTO;
  uint32_t t_switch_ = 0, t_trim_ = 0, t_verify_ = 0, t_door_ = 0, t_crit_ = 0, t_last_ = 0;
  uint32_t t_sent_ = 0, t_mains_ = 0, t_off_check_ = 0, t_damp_ = 0;
};

// Modbus encoding used by the node and the touchscreen: degC (or %) x 10 as a signed word,
// INT16_MIN for "no reading".
inline int16_t t10(float v) {
  if (std::isnan(v)) return INT16_MIN;
  float x = std::round(v * 10.0f);
  return (int16_t) (x < -32767.0f ? -32767.0f : (x > 32767.0f ? 32767.0f : x));
}
inline float from_t10(int16_t v) { return v == INT16_MIN ? NAN : v / 10.0f; }

// One controller per node.  Kept here rather than in an ESPHome `globals:` entry because ESPHome
// declares globals before it includes this file.
inline Controller &controller() {
  static Controller c;
  return c;
}
inline Outputs &last_outputs() {
  static Outputs o;
  return o;
}

// Names for logs and the touchscreen.
inline const char *state_name(uint8_t st) {
  switch (st) {
    case ST_STARTING: return "Starting";
    case ST_COOLING: return "Cooling";
    case ST_IDLE: return "Idle";
    case ST_ON: return "On";
    case ST_ECO_OFF: return "Eco off";
    case ST_OFF: return "Off";
    case ST_NOT_COOLING: return "Not cooling";
    case ST_NO_POWER: return "No AC power";
    case ST_CRITICAL: return "CRITICAL";
    default: return "?";
  }
}

}  // namespace sra
