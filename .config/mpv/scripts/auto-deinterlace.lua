-- This script checks whether current video is interlaced when:
-- 1. new file is loaded
-- 2. on seek
-- 3. when you manually toggle deinterlace on/off with assigned keybind
-- and automatically sets deinterlace on/off.
-- 
-- This won't let you set 'deinterlace:yes' for progressive video and
-- set 'deinterlace:no' for interlaced video with assigned keybind as it
-- checks if the value you set is correct every time you manually change it with assigned keybind.
--
--However this will let you switch on video filter bwdif with keybind "ctrl+shift+d"
--if the video isn't recognized as interlaced - at the same time it will switch off hwdec
--as it seems not to be working correctly with bwdif on.
--Above can be reverted with keybind "ctrl+d" and will be automatically reverted at the end-file event.
--PLEASE NOTE: if it is reverted it will set hwdec to "auto-safe" - when you'd like different behaviour
--you need to change lines below, which contain: 'mp.set_property("hwdec", "auto-safe")' to:
--'mp.set_property("hwdec", "*your desired value")'.



function deint()
	if mp.get_property("video-frame-info/interlaced") == "yes"
	or mp.get_property("video-frame-info/tff") == "yes"
		then mp.set_property("deinterlace", "yes")
	else
		mp.set_property("deinterlace", "no")
	end
end

function vf_off_without_msg()
	mp.set_property("vf", "")
	mp.set_property("hwdec", "auto-safe")
end

function vf_off_with_msg()
	mp.set_property("vf", "")
	mp.set_property("hwdec", "auto-safe")
	mp.osd_message('all video filters switched OFF')
end

function deint_vf_bwdif()
	if mp.get_property("deinterlace") == "yes"
		then return
	else
		mp.set_property("hwdec", "no")
		mp.set_property("vf", "lavfi=bwdif")		
		mp.osd_message('BWDIF deinterlace filter switched ON')
	end
end


mp.register_event("playback-restart", deint)
mp.observe_property("deinterlace", "bool", deint)
mp.register_event("end-file", vf_off_without_msg)
mp.add_key_binding("ctrl+d", vf_off_with_msg)
mp.add_key_binding("ctrl+shift+d", deint_vf_bwdif)

