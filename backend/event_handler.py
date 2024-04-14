from typing_extensions import override
from openai import AssistantEventHandler

class EventHandler(AssistantEventHandler):    
  
  def __init__(self):
    self.text_delta_values = ''
    self.image_data = ''
    self.image_id = ''
    super().__init__()
    
  @override
  def on_text_created(self, text) -> None:
    print(f"\nassistant > ", end="", flush=True)
      
  @override
  def on_text_delta(self, delta, snapshot):
    print(delta.value, end="", flush=True)
    self.text_delta_values+=delta.value
      
  def on_tool_call_created(self, tool_call):
    print(f"\nassistant > {tool_call.type}\n", flush=True)
  
  def on_tool_call_delta(self, delta, snapshot):
    if delta.type == 'code_interpreter':
      if delta.code_interpreter.input:
        print(delta.code_interpreter.input, end="", flush=True)
      if delta.code_interpreter.outputs:
        print(f"\n\noutput >", flush=True)
        for output in delta.code_interpreter.outputs:
          print(output.type)
          if output.type == "logs":
            print(f"\n{output.logs}", flush=True)
          elif output.type == "image":
            image_id = output.image.file_id
            self.image_id = image_id