import base64
import io

import pandas as pd
from langchain_core.tools import BaseTool
from langchain_experimental.tools import PythonAstREPLTool
from matplotlib import pyplot as plt

from backend.model.output.plot_output import PlotOutput
from backend.model.output.text_output import TextOutput
from backend.model.output.error_output import ErrorOutput


class PythonTool(BaseTool):
    name: str = "python_interpreter"
    description: str = (
        "Use this to execute python code for data analysis or visualization. "
        "It can inspect data, perform calculations, or generate plots. "
        "The user's DataFrame is available as the `df` variable."
    )
    df: pd.DataFrame

    class Config:
        arbitrary_types_allowed = True

    def _run(self, code: str) -> dict:
        original_show = plt.show
        plt.show = lambda: None

        try:
            repl = PythonAstREPLTool(locals={"df": self.df})
            result = repl.run(code)

            if plt.get_fignums():
                buffer = io.BytesIO()
                plt.savefig(buffer, format='png', bbox_inches='tight')
                image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

                output = PlotOutput(
                    data=image_base64,
                    caption=str(result) if result else "Generated plot."
                )
            else:
                output = TextOutput(data=str(result))

            return output.model_dump()
        except Exception as e:
            return ErrorOutput(message=f"Error executing code: {str(e)}").model_dump()
        finally:
            plt.close('all')
            plt.show = original_show