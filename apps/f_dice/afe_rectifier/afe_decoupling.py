import math

VBUS_FBK_V = 600
MAX_FREQUENCY = 500
OMEGA = MAX_FREQUENCY * 2 * math.pi
M_Lm_uH = 5000

if VBUS_FBK_V:
	omega_l = OMEGA * M_Lm_uH # [rad/s * uH]

	# calcolo di Vd_decoupling, dipendente dalla Iq_fbk (ma si usa la Iq_ref perche' la Iq_ref e' piu' rapida a crescere)
	I_ref_A_lsh3 = divshx((current_mA(motor_, motor_->CL_Iq_ref) * 131), 14);		// ((I_fbk[mA] * 131) >> 14) = (I_fbk[A] << 3)

	// omega_l[rad/s*H] = omega_l[rad/s*uH]/ 10^6
	// 1/10^6 =  mul (67)	 sh (26)	 err% (0.1622200012206986) quindi:
	// omega_l[rad/s*H] = (omega_l[rad/s*uH] * 67)>>26

	Vbuffer_V = divshx((omega_l * 67 * I_ref_A_lsh3),26+3);
	motor_->CL_Vd_decoupling = voltage_V_2_iu(Vbuffer_V, Smps->Vbus_fbk_V);

	// calcolo di Vq_decoupling, dipendente dalla Id_fbk (ma si usa la Id_ref)
	I_ref_A_lsh3 = divshx((current_mA(motor_, motor_->CL_Id_ref) * 131), 14);		// ((I_fbk[mA] * 131) >> 14) = (I_fbk[A] << 3)
	Vbuffer_V = divshx((omega_l * I_ref_A_lsh3),3);
	motor_->CL_Vq_decoupling = voltage_V_2_iu(Vbuffer_V, Smps->Vbus_fbk_V);
