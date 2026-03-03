import textual

class NBodyApp(textual.App):
    async def on_mount(self):
        await self.view.dock(textual.Header(), edge="top")
        await self.view.dock(textual.Footer(), edge="bottom")
        await self.view.dock(textual.Text("N-Body Simulation Running..."), edge="left")
if __name__ == "__main__":
    NBodyApp.run() 