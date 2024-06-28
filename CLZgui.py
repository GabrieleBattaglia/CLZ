# CLZ by Gabriele Battaglia
# GUI by ChatGPT4o on 25/06/2024.
import wx
import pickle

class CollectionApp(wx.Frame):

	def __init__(self, *args, **kw):
		super(CollectionApp, self).__init__(*args, **kw)

		self.clz = "CLZ-" + "default".lower().strip()
		self.collection_modified = False
		self.load_collection()
		self.original_count = len(self.collection)
		self.InitUI()

	def InitUI(self):
		panel = wx.Panel(self)

		# Set background color
		panel.SetBackgroundColour('#013220')  # Very dark green

		vbox = wx.BoxSizer(wx.VERTICAL)

		# Menu bar
		menubar = wx.MenuBar()
		fileMenu = wx.Menu()
		newItem = fileMenu.Append(wx.ID_NEW, 'Nuova Collezione', 'Crea una nuova collezione')
		openItem = fileMenu.Append(wx.ID_OPEN, 'Apri Collezione', 'Apri una collezione salvata')
		mergeItem = fileMenu.Append(wx.ID_ANY, 'Unisci Collezione', 'Unisci una seconda collezione')
		saveItem = fileMenu.Append(wx.ID_SAVE, 'Salva in Testo', 'Salva la collezione in un file di testo')
		saveAsItem = fileMenu.Append(wx.ID_ANY, 'Salva con Nome', 'Salva la collezione con un nome diverso')
		fileMenu.AppendSeparator()
		quitItem = fileMenu.Append(wx.ID_EXIT, 'Esci', 'Esci dall\'applicazione')

		menubar.Append(fileMenu, '&File')
		self.SetMenuBar(menubar)

		self.Bind(wx.EVT_MENU, self.OnNewCollection, newItem)
		self.Bind(wx.EVT_MENU, self.OnOpen, openItem)
		self.Bind(wx.EVT_MENU, self.OnMerge, mergeItem)
		self.Bind(wx.EVT_MENU, self.OnSave, saveItem)
		self.Bind(wx.EVT_MENU, self.OnSaveAs, saveAsItem)
		self.Bind(wx.EVT_MENU, self.OnQuit, quitItem)

		# New Item Input
		self.newItemTxt = wx.TextCtrl(panel, style=wx.TE_PROCESS_ENTER)
		self.newItemTxt.SetForegroundColour('#FFFFFF')  # White
		self.newItemTxt.SetBackgroundColour('#013220')  # Very dark green

		self.Bind(wx.EVT_TEXT_ENTER, self.OnAddItem, self.newItemTxt)
		self.newItemTxt.SetFocus()

		# Collection List
		self.collectionList = wx.ListBox(panel, style=wx.LB_SINGLE)
		self.collectionList.SetForegroundColour('#FFD700')  # Yellow
		self.collectionList.SetBackgroundColour('#013220')  # Very dark green

		self.collectionList.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)

		# Collection Info
		collectionInfoLbl = wx.StaticText(panel, label='Info collezione:')
		collectionInfoLbl.SetForegroundColour('#ADD8E6')  # Light blue
		self.collectionInfoTxt = wx.TextCtrl(panel)
		self.collectionInfoTxt.SetForegroundColour('#ADD8E6')  # Light blue
		self.collectionInfoTxt.SetBackgroundColour('#013220')  # Very dark green

		# Arrange controls
		vbox.Add(self.newItemTxt, 0, wx.EXPAND | wx.ALL, 10)
		vbox.Add(self.collectionList, 1, wx.EXPAND | wx.ALL, 10)

		hbox3 = wx.BoxSizer(wx.HORIZONTAL)
		hbox3.Add(collectionInfoLbl, 0, wx.RIGHT, 10)
		hbox3.Add(self.collectionInfoTxt, 1)
		vbox.Add(hbox3, 0, wx.EXPAND | wx.ALL, 10)

		panel.SetSizer(vbox)
		self.update_collection_list()
		self.update_collection_info()

		self.Bind(wx.EVT_CLOSE, self.OnClose)

		self.SetSize((400, 300))
		self.SetTitle('Gestione Collezioni')
		self.Centre()

		# Set tab order
		self.newItemTxt.MoveBeforeInTabOrder(self.collectionList)
		self.collectionList.MoveBeforeInTabOrder(self.collectionInfoTxt)

	def load_collection(self):
		try:
			with open(self.clz + ".gbd", "rb") as f:
				self.collection = pickle.load(f)
		except IOError:
			self.collection = []

	def save_collection(self, filename=None):
		if filename is None:
			filename = self.clz + ".gbd"
		with open(filename, "wb") as f:
			pickle.dump(self.collection, f, protocol=pickle.HIGHEST_PROTOCOL)

	def update_collection_list(self):
		self.collectionList.Set(self.collection)

	def update_collection_info(self):
		current_count = len(self.collection)
		total_chars = sum(len(item) for item in self.collection)
		change = current_count - self.original_count
		percentage_change = (change / self.original_count) * 100 if self.original_count != 0 else 0
		info = (f"Origine: {self.original_count} --> ({percentage_change:+.2f}%) --> {current_count} ora.")
		self.collectionInfoTxt.SetValue(info)

	def OnNewCollection(self, event):
		# Save the current collection
		if self.collection_modified:
			self.save_collection()

		# Clear the collection and reset
		self.collection = []
		self.original_count = 0
		self.clz = "CLZ-" + "default".lower().strip()
		self.collection_modified = False
		self.update_collection_list()
		self.update_collection_info()

	def OnOpen(self, event):
		with wx.FileDialog(self, "Scegli il file della collezione da aprire", wildcard="GBD files (*.gbd)|*.gbd",
						   style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:

			if fileDialog.ShowModal() == wx.ID_CANCEL:
				return

			pathname = fileDialog.GetPath()
			try:
				with open(pathname, 'rb') as f:
					self.collection = pickle.load(f)
					self.clz = pathname.rsplit('.', 1)[0]  # Update collection name based on file name
					self.original_count = len(self.collection)
					self.update_collection_list()
					self.update_collection_info()
			except Exception as e:
				wx.LogError("Non posso caricare il file '%s'." % pathname)

	def OnMerge(self, event):
		with wx.FileDialog(self, "Scegli il file della collezione da unire", wildcard="GBD files (*.gbd)|*.gbd",
						   style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:

			if fileDialog.ShowModal() == wx.ID_CANCEL:
				return

			pathname = fileDialog.GetPath()
			try:
				with open(pathname, 'rb') as f:
					new_collection = pickle.load(f)
					self.collection.extend(new_collection)
					self.collection = list(set(self.collection))  # Ensure unique elements
					self.collection.sort()
					self.collection_modified = True
					self.update_collection_list()
					self.update_collection_info()
			except Exception as e:
				wx.LogError("Non posso caricare il file '%s'." % pathname)

	def OnSave(self, event):
		self.save_collection()

	def OnSaveAs(self, event):
		with wx.FileDialog(self, "Salva la collezione con un nome diverso", wildcard="GBD files (*.gbd)|*.gbd",
						   style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as fileDialog:

			if fileDialog.ShowModal() == wx.ID_CANCEL:
				return

			pathname = fileDialog.GetPath()
			try:
				self.save_collection(pathname)
			except Exception as e:
				wx.LogError("Non posso salvare il file '%s'." % pathname)

	def OnQuit(self, event):
		self.Close()

	def OnAddItem(self, event):
		new_item = self.newItemTxt.GetValue().strip().capitalize()
		if new_item and new_item not in self.collection:
			self.collection.append(new_item)
			self.collection.sort()
			self.collection_modified = True
			self.update_collection_list()
			self.update_collection_info()
		else:
			wx.MessageBox('Elemento già presente o invalido', 'Errore', wx.OK | wx.ICON_ERROR)
		self.newItemTxt.Clear()

	def OnKeyDown(self, event):
		if event.GetKeyCode() == wx.WXK_DELETE:
			selection = self.collectionList.GetSelection()
			if selection != wx.NOT_FOUND:
				self.collection.pop(selection)
				self.collection_modified = True
				self.update_collection_list()
				self.update_collection_info()
		else:
			event.Skip()

	def OnClose(self, event):
		if self.collection_modified:
			self.save_collection()
		self.Destroy()

def main():
	app = wx.App()
	ex = CollectionApp(None)
	ex.Show()
	app.MainLoop()

if __name__ == '__main__':
	main()
