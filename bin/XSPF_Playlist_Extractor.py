#!/usr/bin/python

# XSPF playlist extractor
#
# Author: Srinivas Gowda
# website: solancer.com
# Email: srinivas@solancer.com
# Blog: solancer.blogspot.com


import gtk
import xml.etree.ElementTree as ET
import shutil
import re
import urllib2
import os

class PlaylistParser():

	def get_playlist(self):
		dialog = gtk.FileChooserDialog("Open..",
		                               None,
		                               gtk.FILE_CHOOSER_ACTION_OPEN,
		                               (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
		                                gtk.STOCK_OPEN, gtk.RESPONSE_OK))
		dialog.set_default_response(gtk.RESPONSE_OK)
		dialog.set_title('Select XSPF Playlist')
		response = dialog.run()
		if response == gtk.RESPONSE_OK:
		    return  dialog.get_filename()
		elif response == gtk.RESPONSE_CANCEL:
		    return 'Closed, no files selected'
		dialog.destroy()


	def get_destination(self):
		dialog = gtk.FileChooserDialog("Open..",
		                               None,
		                               gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER,
		                               (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
		                                gtk.STOCK_OPEN, gtk.RESPONSE_OK))
		dialog.set_default_response(gtk.RESPONSE_OK)
		response = dialog.run()
		if response == gtk.RESPONSE_OK:
		    return  dialog.get_filename()
		elif response == gtk.RESPONSE_CANCEL:
		    return 'Closed, no files selected'
		dialog.destroy()

	def parse_list(self, playlist):
		tree = ET.parse(playlist)
		song_files = []
		for e in tree.iter(tag='{http://xspf.org/ns/0/}location'):
			clean = re.sub(r'file:///', '/', e.text)
			
			# ENABLES FILES TO HAVE SPACES IN NAME
			decoded = urllib2.unquote(clean)
			song_files.append(decoded)
		if song_files != None:
			return song_files
		else:
			print "Something went wrong, check the playlist file and try again"

	def push_files(self,song_list, destination):
		# SETUP COUNTER FOR TRACK NUMBERS
		i=1
		for song in song_list:
			# GET FILENAME OF SONG AND RENAME IT WITH TRACK NUMBERS
			head, tail = os.path.split(song)
			shutil.copy2(song, destination + "/" + "%02d" % i + "_" + tail)
			i=i+1

	def msg_dialog(self, info):
		msg_dialog = gtk.MessageDialog(parent=None, 
                            flags=0, 
                            type=gtk.MESSAGE_INFO, 
                            buttons=gtk.BUTTONS_OK, 
                            message_format=None)
		msg_dialog.set_markup(info)
		return msg_dialog

if __name__ == "__main__":
	plp = PlaylistParser()

	intro_dialog = plp.msg_dialog("This Script extracts XSPF playlist files to a specified folder")
	intro_dialog.run()
	intro_dialog.destroy()

	info_select_playlist = plp.msg_dialog("First select the XSPF playlist file.")
	info_select_playlist.run()
	info_select_playlist.destroy()
	playlist = plp.get_playlist()

	info_select_folder = plp.msg_dialog("Now select the folder you want to save the files to.")
	info_select_folder.run()
	info_select_folder.destroy()

	destination = plp.get_destination()
	song_list = plp.parse_list(playlist)
	plp.push_files(song_list, destination)

	info_job_done = plp.msg_dialog("Done copying %s files to %s"%((str(len(song_list)), destination)))
	info_job_done.run()
	info_job_done.destroy()
	

