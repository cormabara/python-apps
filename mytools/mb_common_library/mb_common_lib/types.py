"""
Library file with all defines and macro about data types
"""

U32_MAX = (2**32)-1     # Max for unsigned 32 integer
S32_MAX = (2**31)-1     # Max for signed 32 integer

def U32(v_):
	return int(v_ + (1 << 32))  

def S32(v_):
	return int(v_)  
