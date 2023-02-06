# Defined interactively
function lbformat
    ssort && isort . && black ***.py && vulture . | grep -vE 'report_callback_exception|_get_coord_offset_from_monitor|get_monitor_from_coord|monitor|breakpointhook|handlers|option_string'
end
