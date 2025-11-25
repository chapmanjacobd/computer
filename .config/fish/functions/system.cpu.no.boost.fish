# Defined interactively
function system.cpu.no.boost
    echo 1 | sudo tee /sys/devices/system/cpu/intel_pstate/no_turbo
    echo 0 | sudo tee /sys/devices/system/cpu/cpufreq/boost
    echo power | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/energy_performance_preference
end
