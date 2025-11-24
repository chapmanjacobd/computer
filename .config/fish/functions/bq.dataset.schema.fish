# Defined in /tmp/fish.hQq6Ur/bq_fetch_dataset_schema.fish @ line 2
function bq.dataset.schema --argument ds
    for i in (bq ls -n 9999 --format="json" $ds | jq -r '.[].tableReference.tableId')
        bq show --schema --format=prettyjson $ds.$i >$ds.$i &
    end
end
