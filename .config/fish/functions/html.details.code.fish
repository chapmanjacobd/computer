# Defined interactively
function html.details.code
    echo -n '<details>
<summary></summary>

```plain
'
    cb
    echo '
```

</details>'
end
