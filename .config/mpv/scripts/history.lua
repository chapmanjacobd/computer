local HISTFILE = (os.getenv('APPDATA') or os.getenv('HOME')..'/.config')..'/mpv/history.log';

local remember = function()
    local title, fp;

    title = mp.get_property('media-title');
    title = (title == mp.get_property('filename') and '' or (' (%s)'):format(title));

    fp = io.open(HISTFILE, 'a+');
    fp:write(('[%s] %s%s\n'):format(os.date('%Y-%m-%d %X'), mp.get_property('path'), title));
    fp:close();
end

mp.register_event('file-loaded', remember)
