LOADING_MESSAGE = "If you leave this page you can come back later! You will get an email when this is done if it takes more than a minute."

# Slurm job states
PENDING = "PENDING"
RUNNING = "RUNNING"
CONFIGURING = "CONFIGURING"
COMPLETING = "COMPLETING"
FAILED = "FAILED"
COMPLETED = "COMPLETED"
UNKNOWN = "UNKNOWN"
# Slurm job state reasons
LAUNCH_FAILED_REASON = "JobHeldUser"
LAUNCH_FAILED_DESC = "launch failed requeued held"

SLURM_JOB_STATUS_CHECK_PERIOD = 60
SLURM_REST_API_USER = "basechem"

TORSION_ALERTS_TOTAL_ENERGY_THRESHOLD = 0.1
# This is the name of the property with torsion alerts data as returned by the Mayachemtools script
TORSION_ALERTS_PROP = "TorsionAlerts(RotBondIndices TorsionIndices TorsionAngle Energy EnergyLowerBoundCI EnergyUpperBoundCI HierarchyClass HierarchySubClass TorsionRule EnergyMethod AngleNotObserved MaxSingleEnergyAlert)"
TORSION_ALERTS_ENERGY_PROP = "TotalEnergy"
ADMIN_FAILURE = "Admin Failure"
ADMIN_NOTIFICATION = "Admin Notification"

# IB Model Names
IB_LOGD = "generic_logd"
IB_HLM = "generic_hlm"
IB_RLM = "generic_rlm"
IB_PERM = "generic_perm_mdck_mdr1"
IB_EFFLUX = "generic_efflux_mdck_mdr1"
IB_KSOL = "generic_kinetic_solubility"
IB_APKA = "generic_apka"
IB_BPKA = "generic_bpka"

ALL_IB_MODELS = [IB_LOGD, IB_HLM, IB_RLM, IB_PERM, IB_EFFLUX, IB_KSOL, IB_APKA, IB_BPKA]
