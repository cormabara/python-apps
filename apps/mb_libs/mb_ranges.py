""" \brief verifica del segnale se fuori dai limiti
 *
 *  \param [in] val_ (s32) valore da verificare
 *  \param [in] min_ (s32) limite minimo
 *  \param [in] max_ (s32) limite massimo
 *  \return 1 se il valore e' fuori dai limiti, altrimenti 0
 *
 *  \details More details
 """
from mb_types import S32_MAX, S32_MIN


def check_out_range(value_, min_, max_):
	return (value_ < min_) or (value_ > max_)

"""
 *  brief Saturazione del segnale se fuori dai limiti
 *
 *  \param [in] val_ (s32) valore da verificare
 *  \param [in] min_ (s32) limsaturate_out_of_rangeite minimo
 *  \param [in] max_ (s32) limite massimo
 *  return Il valore in ingresso è limitato tra min_ e max_
 *
 *  \details More details
 """
def saturate_out_of_range(value_, min_, max_):
	retval = value_
	if retval < min_:
		retval = min_
	elif retval > max_:
		retval = max_
	return retval

def saturate_out_of_range_smart(value_,v1_,v2_):
	min = v2_ if v1_ > v2_ else v1_
	max = v1_ if v1_ > v2_ else v2_
	if value_ < min:
		value_ = min;
	elif value_ > max:
		value_ = max;
	return value_

def wrap_out_of_range(value_, min_, max_, delta_):
	if value_ < min_:
		value_ += delta_
	elif value_ > max_:
		value_ -= delta_
	return value_


def check_s32(v_):
	return check_out_range(v_, S32_MIN, S32_MAX)