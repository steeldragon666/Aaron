// C wrapper so tools/sim_controller.py can drive the real controller through ctypes.
//   g++ -std=c++17 -O2 -shared -fPIC -I../components/sra_control sra_capi.cpp -o libsra.so
#include "sra_control.h"

extern "C" {

void *sra_new() { return new sra::Controller(); }
void sra_free(void *c) { delete static_cast<sra::Controller *>(c); }
void sra_get_settings(void *c, sra::Settings *s) { *s = static_cast<sra::Controller *>(c)->s; }
void sra_set_settings(void *c, const sra::Settings *s) { static_cast<sra::Controller *>(c)->s = *s; }
void sra_step(void *c, const sra::Inputs *in, uint32_t now, sra::Outputs *out) {
  *out = static_cast<sra::Controller *>(c)->step(*in, now);
}
void sra_request_send(void *c) { static_cast<sra::Controller *>(c)->request_send(); }
// sizes for a layout check on the Python side: 0 Settings, 1 Inputs, 2 Outputs
unsigned sra_sizeof(int which) {
  return which == 0 ? sizeof(sra::Settings) : which == 1 ? sizeof(sra::Inputs) : sizeof(sra::Outputs);
}

}  // extern "C"
