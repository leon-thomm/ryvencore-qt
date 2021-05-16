"""
-------- DEPRECATED AND NOT USED ANYMORE --------
"""


from ..Base import Base


class Log(Base):

    def __init__(self, title: str):
        Base.__init__(self)

        self.title: str = title
        self.lines: [str] = []
        self.current_lines: [str] = []
        self.enabled_: bool = True

    def write(self, *args):
        if not self.enabled_:
            return

        s = ''
        for arg in args:
            s += ' '+str(arg)
        self.lines.append(s)
        self.current_lines.append(s)

    def clear(self):
        self.current_lines.clear()

    def disable(self):
        self.enabled_ = False

    def enable(self):
        self.enabled_ = True

    def save_to_file(self, filepath: str, all_lines=True):
        """Saves the log data to a file. If all_lines is false, it only saves the current (not cleared) lines."""
        f = open(filepath)
        f.write(('\n'.join(self.lines)) if all_lines else ('\n'.join(self.current_lines)))
        f.close()
