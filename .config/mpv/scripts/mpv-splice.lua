-- -----------------------------------------------------------------------------
--
-- MPV Splice
-- URL: https://github.com/pvpscript/mpv-video-splice
--
-- Requires: ffmpeg
--
-- Description:
--
-- This script provides the ability to create video slices by grabbing two
-- timestamps, which generate a slice from timestamp A[i] to timestamp B[i],
-- e.g.:
-- 	-> Slice 1: 00:10:34.25 -> 00:15:00.00.
-- 	-> Slice 2: 00:23:00.84 -> 00:24:10.00.
-- 	...
-- 	-> Slice n: 01:44:22.47 -> 01:56:00.00.
--
-- Then, all the slices from 1 to n are joined together, creating a new
-- video.
--
-- The output file will appear at the directory that the mpv command was ran,
-- or in the environment variable set for it (see Environment variables below)
--
-- Note: This script prevents the mpv player from closing when the video ends,
-- so that the slices don't get lost. Keep this in mind if there's the option
-- 'keep-open=no' in the current config file.
--
-- Note: This script will also silence the terminal, so the script messages
-- can be seen more clearly.
--
-- -----------------------------------------------------------------------------
--
--
-- Usage:
--
-- In the video screen, press Alt + T to grab the first timestamp and then
-- press Alt + T again to get the second timestamp. This process will generate
-- a time range, which represents a video slice. Repeat this process to create
-- more slices.
--
-- To see all the slices made, press Alt + P. All of the slices will appear
-- in the terminal in order of creation, with their corresponding timestamps.
-- Incomplete slices will show up as 'Slice N in progress', where N is the
-- slice number.
--
-- To reset an incomplete slice, press Alt + R. If the first part of a slice
-- was created at the wrong time, this will reset the current slice.
--
-- To delete a whole slice, start the slice deletion mode by pressing Alt + D.
-- When in this mode, it's possible to press Alt + NUM, where NUM is any
-- number between 0 inclusive and 9 inclusive. For each Alt + NUM pressed, a
-- number will be concatenated to make the final number referring to the slice
-- to be removed, then press Alt + D again to stop the slicing deletion mode
-- and delete the slice corresponding to the formed number.
--
-- Example 1: Deleting slice number 3
-- 	-> Alt + D 	# Start slice deletion mode
-- 	-> Alt + 3	# Concatenate number 3
-- 	-> Alt + D	# Exit slice deletion mode
--
-- Example 2> Deleting slice number 76
-- 	-> Alt + D 	# Start slice deletion mode
-- 	-> Alt + 7	# Concatenate number 7
-- 	-> Alt + 6	# Concatenate number 6
-- 	-> Alt + D	# Exit slice deletion mode
--
-- To fire up ffmpeg, which will slice up the video and concatenate the slices
-- together, press Alt + C. It's important that there are at least one
-- slice, otherwise no video will be created.
--
-- Note: No cut will be made unless the user presses Alt + C.
-- Also, the original video file won't be affected by the cutting.
--
--
-- -----------------------------------------------------------------------------
--
--
-- Log level:
--
-- Everytime a timestamp is grabbed, a text will appear on the screen showing
-- the selected time.
-- When Alt + P is pressed, besides showing the slices in the terminal,
-- it will also show on the screen the total number of cuts (or slices)
-- that were made.
-- When the actual cutting and joining process begins, a message will be shown
-- on the screen and the terminal telling that it began. When the process ends,
-- a message will appear on the screen and the terminal displaying the full path
-- of the generated video. It will also appear a message in the terminal telling
-- that the process ended.
--
-- Note: Every message that appears on the terminal has the log level of 'info'.
--
--
-- -----------------------------------------------------------------------------
--
--
-- Environment Variables:
--
-- This script uses environment variables to allow the user to
-- set the temporary location of the video cuts and for setting the location for
-- the resulting video.
--
-- To set the temporary directory, set the variable MPV_SPLICE_TEMP;
-- e.g.: export MPV_SPLICE_TEMP="$HOME/temporary_location"
--
-- To set the video output directory, set the variable MPV_SPLICE_OUTPUT;
-- e.g.: export MPV_SPLICE_OUTPUT="$HOME/output_location"
--
-- Make sure the directories set in the variables really exist, or else the
-- script might fail.
--
-- -----------------------------------------------------------------------------

--------------------------------------------------------------------------------
-- Importing the mpv libraries

local mp = require 'mp'
local msg = require 'mp.msg'
local opt = require 'mp.options'

--------------------------------------------------------------------------------
-- Default variables

local SCRIPT_NAME = "mpv-splice"

local splice_options = {
	tmp_location = "/tmp/XXXX",
	output_location = '/mnt/d/79_Cinemagraph/Clips/mpv' or mp.get_property("working-directory")
}
opt.read_options(splice_options, SCRIPT_NAME)


local ffmpeg = "ffmpeg -hide_banner -loglevel warning"

local times = {}
local start_time = nil
local remove_val = ""

local exit_time = 0

--------------------------------------------------------------------------------

function notify(duration, ...)
	local args = {...}
	local text = ""

	for i, v in ipairs(args) do
		text = text .. tostring(v)
	end

	msg.info(text)
	mp.command(string.format("show-text \"%s\" %d 1",
		text, duration))
end

local function get_time()
	local time_in_secs = mp.get_property_number('time-pos')

	local hours = math.floor(time_in_secs / 3600)
	local mins = math.floor((time_in_secs - hours * 3600) / 60)
	local secs = time_in_secs - hours * 3600 - mins * 60

	local fmt_time = string.format('%02d:%02d:%05.2f', hours, mins, secs)

	return fmt_time
end

function put_time()
	local time = get_time()
	local message = ""

	if not start_time then
		start_time = time
		message = "[START TIMESTAMP]"
	else
		--times[#times+1] = {
		table.insert(times, {
			t_start = start_time,
			t_end = time
		})
		start_time = nil

		message = "[END TIMESTAMP]"
	end

	notify(2000, message, ": ", time)
end

function show_times()
	notify(2000, "Total cuts: ", #times)

	for i, obj in ipairs(times) do
		msg.info("Slice", i, ": ", obj.t_start, " -> ", obj.t_end)
	end
	if start_time then
		notify(2000, "Slice ", #times+1, " in progress.")
	end
end

function reset_current_slice()
	if start_time then
		notify(2000, "Slice ", #times+1, " reseted.")

		start_time = nil
	end
end

function delete_slice()
	if remove_val == "" then
		notify(2000, "Entered slice deletion mode.")

		-- Add shortcut keys to the interval {0..9}.
		for i=0,9,1 do
			mp.add_key_binding("Alt+" .. i, "num_key_" .. i,
				function()
					remove_val = remove_val .. i
					notify(1000, "Slice to remove: "
						.. remove_val)
				end
			)
		end
	else
		-- Remove previously added shortcut keys.
		for i=0,9,1 do
			mp.remove_key_binding("num_key_" .. i)
		end

		remove_num = tonumber(remove_val)
		if #times >= remove_num and remove_num > 0 then
			table.remove(times, remove_num)
			notify(2000, "Removed slice ", remove_num)
		end

		remove_val = ""

		msg.info("Exited slice deletion mode.")
	end
end

-- function prevent_quit(name)
-- 	if start_time then
-- 		if os.time() - exit_time <= 2 then
-- 			mp.command(name)
-- 		else
-- 			exit_time = os.time()
-- 		end
-- 		notify(3000, "Slice has been marked. Press again to quit")
-- 	else
-- 		mp.command(name)
-- 	end
-- end


-- mp.add_key_binding('q', "quit", function()
-- 	prevent_quit("quit")
-- end)
-- mp.add_key_binding('Shift+q', "quit-watch-later", function()
-- 	prevent_quit("quit-watch-later")
-- end)

function process_video()
	local alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
	local rnd_size = 10

	local pieces = {}

	-- Better seed randomization
	math.randomseed(os.time())
	math.random(); math.random(); math.random()

	if times[#times] then
		local tmp_dir = io.popen(string.format("mktemp -d %s",
			splice_options.tmp_location)):read("*l")
		local input_file = mp.get_property("path")
		local ext = string.gmatch(input_file, ".*%.(.*)$")()

		local rnd_str = ""
		for i=1,rnd_size,1 do
			local rnd_index = math.floor(math.random() * #alphabet + 0.5)
			rnd_str = rnd_str .. alphabet:sub(rnd_index, rnd_index)
		end

		local output_file = string.format("%s/%s_%s_cut.%s",
			splice_options.output_location,
			mp.get_property("filename/no-ext"),
			rnd_str, ext)

		local cat_file_name = string.format("%s/%s", tmp_dir, "concat.txt")
		local cat_file_ptr = io.open(cat_file_name, "w")

		notify(2000, "Process started!")

		for i, obj in ipairs(times) do
			local path = string.format("%s/%s_%d.%s",
				tmp_dir, rnd_str, i, ext)
			cat_file_ptr:write(string.format("file '%s'\n", path))
			os.execute(string.format("%s -ss %s -i \"%s\" -to %s " ..
				"-c copy -copyts -avoid_negative_ts make_zero \"%s\"",
				ffmpeg, obj.t_start, input_file, obj.t_end,
				path))
		end

		cat_file_ptr:close()

		cmd = string.format("%s -f concat -safe 0 -i \"%s\" " ..
			"-c copy \"%s\"",
			ffmpeg, cat_file_name, output_file)
		os.execute(cmd)

		notify(10000, "File saved as: ", output_file)
		msg.info("Process ended!")

		os.execute(string.format("rm -rf %s", tmp_dir))
		msg.info("Temporary directory removed!")
	end
end


mp.add_key_binding('ctrl+t', "put_time", put_time)
mp.add_key_binding('ctrl+p', "process_video", process_video)
mp.add_key_binding('ctrl+r', "reset_current_slice", reset_current_slice)
-- mp.add_key_binding('Alt+t', "show_times", show_times)
-- mp.add_key_binding('ctrl+d', "delete_slice", delete_slice)
