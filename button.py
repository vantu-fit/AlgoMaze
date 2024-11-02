class Button():
	def __init__(self, image, pos, text_input, font, base_color, hovering_color,Himage=None,cSelected=None,selected=0,iSelected=None):
		self.image = image
		self.imSelected=iSelected
		self.cSelected=cSelected
		self.selected=selected
		self.Himage=Himage
		self.x_pos = pos[0]
		self.y_pos = pos[1]
		self.font = font
		self.hover=0
		self.base_color, self.hovering_color = base_color, hovering_color
		self.text_input = text_input
		if self.selected==0:
			self.text = self.font.render(self.text_input, True, self.base_color)
		else: self.text=self.font.render(self.text_input, True, self.cSelected)
		if self.image is None:
			self.image = self.text
		self.rect = self.image.get_rect(center=(self.x_pos, self.y_pos))
		self.text_rect = self.text.get_rect(center=(self.x_pos, self.y_pos))

	def update(self, screen):
		if self.image is not None:
			screen.blit(self.image, self.rect)
		screen.blit(self.text, self.text_rect)
	
	def resetSelection(self):
		self.text=self.font.render(self.text_input, True, self.base_color)
		self.selected=0

	def checkForInput(self, position):
		is_collide=self.rect.collidepoint(position)
		if (is_collide):
			#for StartButton:
			if self.image!=None:
				# print('Start')
				self.image,self.Himage=self.Himage,self.image
			self.selected=1
			self.text=self.font.render(self.text_input, True, self.cSelected)
			print(self.text_input)
		return is_collide

	def changeColor(self, position):
		is_hover = self.rect.collidepoint(position)
		if self.selected==1:
			return
		if is_hover and self.hover==0:
			self.text = self.font.render(self.text_input, True, self.hovering_color)
			self.hover=1
			self.image,self.Himage=self.Himage,self.image
		elif not is_hover and self.hover==1:
			self.hover=0
			# print('not hover',self.hover)
			self.text = self.font.render(self.text_input, True, self.base_color)
			self.image,self.Himage=self.Himage,self.image