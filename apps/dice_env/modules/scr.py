
# @brief Enum con i pissibili stati della macchina SCR

from enum import Enum
from dataclasses import dataclass
from typing import List


class ScrIrqStatus(Enum):
	scrSt_NULL = 0
	scrSt_Start = 1
	scrSt_WaitBoot = 2
	scrSt_WaitPhase = 3
	scrSt_LockPhase_On = 4
	scrSt_LockPhase_Off = 5
	scrSt_FindSequence_On = 6
	scrSt_FindSequence_Off = 7
	scrSt_Gating = 8
	scrSt_Fail = 9


class ScrBridge:

	@dataclass
	class Inputs:
		phU: List[List[int]]
		phV: List[List[int]]
		phW: List[List[int]]

	@dataclass
	class Outputs:
		mainVBus: int

	@dataclass
	class ZeroCross:
		zc_uv = []
		zc_vw = []
		zc_wu = []

	"""" This is the class for the SCR rectifier"""
	def __init__(self):
		self.phU = []
		self.phV = []
		self.phW = []

		self.out_uv = []
		self.out_vw = []
		self.out_wu = []
		self.status = ScrIrqStatus.scrSt_NULL
		self.zeroCross = ScrBridge.ZeroCross()
		self.inputs = ScrBridge.Inputs()

	def SetStimulus(self, phu_, phv_, phw_):
		"""Set the inputs for the SCR and pre-process some intermediate signals """
		self.inputs.phU = phu_
		self.inputs.phV = phv_
		self.inputs.phW = phw_
		InSize = len(self.phU)
		self.out_uv = [0 for i in range(InSize)]
		self.out_vw = [0 for i in range(InSize)]
		self.out_wu = [0 for i in range(InSize)]
		self.zeroCross.zc_uv = [0 for i in range(InSize)]
		self.zeroCross.zc_vw = [0 for i in range(InSize)]
		self.zeroCross.zc_wu = [0 for i in range(InSize)]
		iterator = range(0,len(self.inputs.phU[:, 0]))
		for val in iterator:
			self.SetInput(val, self.inputs.phU[val], self.inputs.phV[val], self.inputs.phW[val])

	def SetInput(self,phase_, phu_, phv_, phw_):
		self.out_uv[phase_] = phv_ - phu_
		self.out_vw[phase_] = phw_ - phv_
		self.out_wu[phase_] = phu_ - phw_
		self.zeroCross.zc_uv[phase_] = int(phv_ >= phu_)
		self.zeroCross.zc_vw[phase_] = int(phw_ >= phv_)
		self.zeroCross.zc_wu[phase_] = int(phu_ >= phw_)

