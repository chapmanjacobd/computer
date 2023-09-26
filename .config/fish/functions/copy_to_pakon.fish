# Defined interactively
function copy_to_pakon
    rsync -auh --info=progress2 --no-inc-recursive --remove-sent-files backup:d/_tixati/ ~/d/75_Moviequeue/from_backup/

    ~/d/75_Moviequeue/from_backup/
    fd '[a-zA-Z]{3,5}-?[0-9]{3}' -x mv {} /mnt/d/69_Taxes/onejav/
    fd '^[a-zA-Z]{3,}-[0-9]{3,5}' -x mv {} /mnt/d/69_Taxes/onejav/
end
