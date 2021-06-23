
#include <Arduino.h>
#include "spo2_algorithm.h"

void maxim_heart_rate_and_oxygen_saturation_b(uint32_t *pun_ir_buffer, int32_t n_ir_buffer_length, uint32_t *pun_red_buffer, int32_t *pn_spo2, int8_t *pch_spo2_valid, int32_t *pn_heart_rate, int8_t *pch_hr_valid, float sampfreq);
