import customtkinter as ctk
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from VALocker import VALocker


from Constants import BRIGHTEN_COLOR, FILE, FRAME, profile
from CustomElements import *
import os

# region: Navigation Frame


class NavigationFrame(ctk.CTkFrame):
    parent: "VALocker"
    theme: dict[str, str]
    nav_buttons: dict[str, ctk.CTkButton] = dict()

    def __init__(self, parent: "VALocker", width: int):
        super().__init__(
            parent, width=width, corner_radius=0, fg_color=parent.theme["foreground"]
        )
        self.parent = parent
        self.theme = parent.theme

        title_frame = ctk.CTkFrame(self, fg_color="transparent")
        title_frame.pack(pady=10)

        title_label_frame = ctk.CTkFrame(title_frame, fg_color="transparent")
        title_label_frame.pack()

        valocker_label_left = ctk.CTkLabel(
            title_label_frame,
            text="VAL",
            fg_color="transparent",
            text_color="#BD3944",
            font=(self.parent.theme["font"], 20),
        )
        valocker_label_left.pack(side=ctk.LEFT)

        valocker_label_right = ctk.CTkLabel(
            title_label_frame,
            text="ocker",
            fg_color="transparent",
            text_color=self.theme["text"],
            font=(self.parent.theme["font"], 20),
        )
        valocker_label_right.pack(side=ctk.LEFT)

        version_label = ctk.CTkLabel(
            title_frame,
            text=f"v{self.parent.VERSION}",
            fg_color="transparent",
            text_color=BRIGHTEN_COLOR(self.theme["text"], 0.5),
            font=(self.parent.theme["font"], 12),
        )
        version_label.pack(pady=0)

        exit_button = ctk.CTkButton(
            self,
            text="Exit",
            font=self.parent.theme["button"],
            fg_color=self.parent.theme["accent"],
            hover_color=self.parent.theme["accent-hover"],
            corner_radius=5,
            hover=True,
            command=self.quit_program,
        )
        exit_button.pack(side=ctk.BOTTOM, pady=10, padx=10, fill=ctk.X)

        normal_buttons = [
            frame for frame in self.parent.frames if frame != FRAME.SETTINGS
        ]

        for frame_enum in normal_buttons:
            self.nav_buttons[frame_enum] = self.create_button(frame_enum)
            self.nav_buttons[frame_enum].pack(fill=ctk.X, side=ctk.TOP)

        # Settings Button
        self.nav_buttons[FRAME.SETTINGS] = self.create_button(FRAME.SETTINGS)
        self.nav_buttons[FRAME.SETTINGS].pack(side=ctk.BOTTOM, fill=ctk.X)

    def create_button(self, frame: FRAME) -> ctk.CTkButton:
        button = ctk.CTkButton(
            self,
            text=frame.value,
            height=40,
            corner_radius=0,
            border_spacing=10,
            anchor=ctk.W,
            fg_color="transparent",
            text_color=self.theme["text"],
            hover_color=BRIGHTEN_COLOR(self.theme["foreground"], 1.5),
            font=self.parent.theme["button"],
            command=lambda frame=frame: self.parent.select_frame(frame),
        )
        return button

    def highlight_button(self, frame: FRAME) -> None:
        """
        Highlights the specified button.

        Parameters:
        - frame (FRAME): The enum of the button to be highlighted.
        """
        for button in self.nav_buttons:
            if frame == button:
                self.nav_buttons[frame].configure(
                    fg_color=BRIGHTEN_COLOR(self.theme["foreground"], 1.5)
                )
            else:
                self.nav_buttons[button].configure(fg_color="transparent")

    def quit_program(self) -> None:
        """
        Quit the program.

        This method is responsible for exiting the program gracefully.
        It calls the `exit` method of the parent object to terminate the application.
        """
        self.parent.exit()


# endregion

# region: Overview Frame


class OverviewFrame(SideFrame):
    agent_dropdown: ThemedDropdown

    def __init__(self, parent: "VALocker"):
        super().__init__(parent)

        # Make each frame take up equal space
        for frame in range(3):
            self.grid_columnconfigure(frame, weight=1)

        # Make the frames take up the entire vertical space
        self.grid_rowconfigure(0, weight=1)

        # Segmented Frames
        left_frame = ThemedFrame(self)
        middle_frame = ThemedFrame(self)
        right_frame = ThemedFrame(self)

        # Grid the frames
        for index, frame in enumerate([left_frame, middle_frame, right_frame]):
            frame.grid(
                row=0,
                column=index,
                sticky="nsew",
                padx=10 if index == 1 else 0,
                pady=10,
            )
            frame.grid_propagate(False)
            frame.columnconfigure(0, weight=1)

        # region: Left Frame
        program_status_label = ThemedLabel(
            left_frame,
            text="Instalocker",
        )
        program_status_label.grid(row=0, column=0, sticky="nsew", padx=10, pady=(10, 0))

        program_status_button = IndependentButton(
            left_frame,
            text=["Running", "Stopped"],
            variable=self.parent.instalocker_thread_running,
            command=lambda: self.parent.toggle_boolean(
                self.parent.instalocker_thread_running
            ),
        )

        program_status_button.grid(
            row=1, column=0, sticky="nsew", padx=10, pady=(0, 10)
        )

        instalocker_status_label = ThemedLabel(left_frame, "Status")
        instalocker_status_label.grid(
            row=2, column=0, sticky="nsew", padx=10, pady=(10, 0)
        )

        instalocker_status_button = DependentButton(
            left_frame,
            variable=self.parent.instalocker_status,
            dependent_variable=self.parent.instalocker_thread_running,
            text=["Locking", "Waiting", "None"],
            command=lambda: self.parent.toggle_boolean(self.parent.instalocker_status),
        )

        instalocker_status_button.grid(
            row=3, column=0, sticky="nsew", padx=10, pady=(0, 10)
        )

        safe_mode_label = ThemedLabel(left_frame, "Safe Mode")
        safe_mode_label.grid(row=4, column=0, sticky="nsew", padx=10, pady=(10, 0))

        safe_mode_button = SplitButton(
            left_frame,
            text_left=["On", "Off"],
            text_right=["Low", "Medium", "High"],
            variable_left=self.parent.safe_mode_enabled,
            variable_right=self.parent.safe_mode_strength,
            command_left=lambda: self.parent.toggle_boolean(
                self.parent.safe_mode_enabled
            ),
            command_right=lambda: self.parent.increment_int(
                self.parent.safe_mode_strength, 3
            ),
        )
        safe_mode_button.grid(row=5, column=0, sticky="nsew", padx=10, pady=(0, 10))

        save_label = ThemedLabel(left_frame, "Current Save")
        save_label.grid(row=6, column=0, sticky="nsew", padx=10, pady=(10, 0))

        save_button = ThemedButton(
            left_frame,
            fg_color=self.theme["foreground-highlight"],
            hover_color=self.theme["foreground-highlight-hover"],
            textvariable=self.parent.current_save_name,
            command=self.redirect_save_files_frame,
        )
        save_button.grid(row=7, column=0, sticky="nsew", padx=10, pady=(0, 10))

        # endregion

        # region: Middle Frame

        agent_label = ThemedLabel(middle_frame, "Selected Agent")
        agent_label.grid(row=0, column=0, sticky="nsew", padx=10, pady=(10, 0))

        self.agent_dropdown = ThemedDropdown(
            middle_frame,
            values=[],
            variable=self.parent.selected_agent,
        )
        self.agent_dropdown.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))

        options_label = ThemedLabel(middle_frame, "Options")
        options_label.grid(row=2, column=0, sticky="nsew", padx=10, pady=(10, 0))

        hover_button = IndependentButton(
            middle_frame,
            text="Hover",
            variable=self.parent.hover,
            command=lambda: self.parent.toggle_boolean(self.parent.hover),
        )
        hover_button.grid(row=3, column=0, sticky="nsew", padx=10)

        random_agent_button = ColorDependentButton(
            middle_frame,
            text="Random Agent",
            variable=self.parent.random_select,
            dependent_variable=self.parent.random_select_available,
            command=lambda: self.parent.toggle_boolean(self.parent.random_select),
        )
        random_agent_button.grid(row=4, column=0, sticky="nsew", padx=10, pady=10)

        map_specific_button = IndependentButton(
            middle_frame,
            text="Map Specific",
            variable=self.parent.map_specific,
            command=lambda: self.parent.toggle_boolean(self.parent.map_specific),
        )
        map_specific_button.grid(row=5, column=0, sticky="nsew", padx=10)

        tools_button = ThemedButton(
            middle_frame,
            text="Tools",
            height=20,
            fg_color=self.theme["foreground-highlight"],
            hover_color=self.theme["foreground-highlight-hover"],
            command=self.redirect_tools_frame,
        )
        tools_button.grid(row=6, column=0, sticky="nsew", padx=10, pady=(10, 5))

        anti_afk_button = IndependentButton(
            middle_frame,
            text="Anti-AFK",
            variable=self.parent.anti_afk,
            command=lambda: self.parent.toggle_boolean(self.parent.anti_afk),
        )
        anti_afk_button.grid(row=7, column=0, sticky="nsew", padx=10)

        # endregion

        # region: Right Frame
        last_lock_label = ThemedLabel(right_frame, "Last Lock")
        last_lock_label.grid(row=0, column=0, sticky="nsew", padx=10, pady=(10, 0))

        last_lock_stat = ThemedLabel(
            right_frame,
            variable=self.parent.last_lock,
        )
        last_lock_stat.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))

        average_lock_label = ThemedLabel(right_frame, "Average Lock")
        average_lock_label.grid(row=2, column=0, sticky="nsew", padx=10, pady=(10, 0))

        average_lock_stat = ThemedLabel(
            right_frame,
            variable=self.parent.average_lock,
        )
        average_lock_stat.grid(row=3, column=0, sticky="nsew", padx=10, pady=(0, 10))

        times_used_label = ThemedLabel(right_frame, "Times Used")
        times_used_label.grid(row=4, column=0, sticky="nsew", padx=10, pady=(10, 0))

        times_used_stat = ThemedLabel(
            right_frame,
            variable=self.parent.times_used,
        )
        times_used_stat.grid(row=5, column=0, sticky="nsew", padx=10, pady=(0, 10))

        # endregion

    def redirect_save_files_frame(self) -> None:
        """
        Redirects the user to the "Save Files" frame.

        This method raises the "Save Files" frame to the top, making it visible to the user.
        """
        self.parent.select_frame(FRAME.SAVE_FILES)

    def redirect_tools_frame(self) -> None:
        """
        Redirects the user to the 'Tools' frame.

        This method raises the 'Tools' frame to the top, making it visible to the user.
        """
        self.parent.select_frame(FRAME.TOOLS)

    def update_dropdown(self, unlocked_agents: list[str]) -> None:
        """
        Updates the options in the agent dropdown based on the unlocked agents.

        Args:
            unlocked_agents (list[str]): A list of unlocked agents.
        """

        self.agent_dropdown.set_values(unlocked_agents)


# endregion

# region: Agent Toggle Frame


class AgentToggleFrame(SideFrame):
    all_variable: ctk.BooleanVar
    none_variable: ctk.BooleanVar

    all_checkbox: ThemedCheckbox
    none_checkbox: ThemedCheckbox

    toggleable_agents: dict[str, ctk.BooleanVar]
    agent_checkboxes: dict[str, ThemedCheckbox]

    def __init__(self, parent: "VALocker"):
        super().__init__(parent)

        top_frame = ThemedFrame(self)
        top_frame.pack(fill=ctk.X, pady=10)
        top_frame.grid_columnconfigure(0, weight=1)
        top_frame.grid_columnconfigure(1, weight=1)

        self.all_variable = ctk.BooleanVar(value=False)
        self.none_variable = ctk.BooleanVar(value=False)

        self.all_checkbox = ThemedCheckbox(
            top_frame,
            text="All",
            variable=self.all_variable,
            command=self.toggle_all,
        )
        self.all_checkbox.grid(row=0, column=0, padx=10, pady=10)

        self.none_checkbox = ThemedCheckbox(
            top_frame,
            text="None",
            variable=self.none_variable,
            command=self.toggle_none,
        )
        self.none_checkbox.grid(row=0, column=1, padx=10, pady=10)

        self.outer_agent_frame = ThemedFrame(self)
        self.outer_agent_frame.pack(expand=True, fill=ctk.BOTH, pady=(0, 10), padx=0)

        self.specific_agent_frame = ThemedFrame(self.outer_agent_frame)
        self.specific_agent_frame.pack(anchor=ctk.CENTER, pady=10, padx=0)

        self.toggleable_agents: dict[str, ctk.BooleanVar] = {
            agent_name: values[0]
            for agent_name, values in self.parent.agent_states.items()
            if len(values) != 1
        }

        NUMBER_OF_COLS = 4

        self.agent_checkboxes = dict()
        for i, (agent_name, variable) in enumerate(self.toggleable_agents.items()):
            row = i // NUMBER_OF_COLS
            col = i % NUMBER_OF_COLS

            self.agent_checkboxes[agent_name] = ThemedCheckbox(
                self.specific_agent_frame,
                text=agent_name.capitalize(),
                variable=variable,
                command=self.toggle_single_agent,
            )

            xpadding = (
                (30, 10) if col == 0 else (10, 30) if col == NUMBER_OF_COLS - 1 else 10
            )
            ypadding = (
                (20, 5)
                if row == 0
                else (
                    (5, 20)
                    if row == len(self.toggleable_agents) // NUMBER_OF_COLS
                    else 5
                )
            )

            self.specific_agent_frame.grid_rowconfigure(row, weight=1)
            self.specific_agent_frame.grid_columnconfigure(col, weight=1)

            self.agent_checkboxes[agent_name].grid(
                row=row, column=col, sticky="nsew", padx=xpadding, pady=ypadding
            )

    def toggle_all(self) -> None:
        """
        Toggles all the agent variables to True if the 'all_variable' is True.
        """
        if not self.all_variable.get():
            return

        for variable in self.toggleable_agents.values():
            variable.set(True)

        self.update_super_checkboxes()

    def toggle_none(self) -> None:
        """
        Toggles the 'none' variable and sets all toggleable agent variables to False.
        """
        if not self.none_variable.get():
            return

        for variable in self.toggleable_agents.values():
            variable.set(False)

        self.update_super_checkboxes()

    def update_super_checkboxes(self) -> None:
        """
        Manages the state of the super checkboxes.

        This method checks if all the toggleable agent variables are checked or unchecked,
        and sets the state of the super checkboxes accordingly. It also enables or disables
        the checkboxes based on the state of the toggleable agent variables.
        """
        # Check if all are checked
        all_checked = all(
            self.toggleable_agents[agent].get() for agent in self.toggleable_agents
        )

        # Check if all are unchecked
        none_checked = all(
            not self.toggleable_agents[agent].get() for agent in self.toggleable_agents
        )

        # Set super checkboxes
        self.all_variable.set(all_checked)
        self.none_variable.set(none_checked)

        # Disable and enable checkboxes
        self.none_checkbox.enable()
        self.all_checkbox.enable()
        if all_checked:
            self.all_checkbox.disable()
        elif none_checked:
            self.none_checkbox.disable()

        self.parent.agent_unlock_status_changed()

    def toggle_single_agent(self) -> None:
        """
        Toggles the state of a single agent.
        """
        self.update_super_checkboxes()

    def on_raise(self) -> None:
        """
        Updates the state of the super checkboxes when the frame is raised.
        """
        self.update_super_checkboxes()


# endregion

# region: Random Select Frame


class RandomSelectFrame(SideFrame):
    all_variable: ctk.BooleanVar
    none_variable: ctk.BooleanVar

    all_checkbox: ThemedCheckbox
    none_checkbox: ThemedCheckbox

    super_role_checkboxes: dict[str, ThemedCheckbox] = dict()
    role_variables: dict[str, ctk.BooleanVar]

    agent_checkboxes: dict[str, dict[str, DependentCheckbox]]

    def __init__(self, parent: "VALocker"):
        super().__init__(parent)

        super_frame = ThemedFrame(self)
        super_frame.pack(fill=ctk.X, pady=10)

        self.exclusiselect_button = IndependentButton(
            super_frame,
            text="ExclusiSelect",
            width=100,  # should be ~120 pixels but when set to 120 it becomes 150 (???)
            variable=self.parent.exclusiselect,
            command=lambda: self.parent.toggle_boolean(self.parent.exclusiselect),
        )
        self.exclusiselect_button.pack(
            side=ctk.LEFT,
            padx=(20, 0),
            pady=10,
        )

        super_checkboxes_frame = ThemedFrame(super_frame, fg_color="transparent")
        super_checkboxes_frame.pack(anchor=ctk.CENTER, fill=ctk.Y, expand=True)

        super_checkboxes_frame.grid_rowconfigure(0, weight=1)

        self.all_variable = ctk.BooleanVar(value=False)
        self.all_checkbox = ThemedCheckbox(
            super_checkboxes_frame,
            text="All",
            variable=self.all_variable,
            command=lambda: self.super_toggle_all(True),
        )
        self.all_checkbox.grid(row=0, column=0)

        self.none_variable = ctk.BooleanVar(value=False)
        self.none_checkbox = ThemedCheckbox(
            super_checkboxes_frame,
            text="None",
            variable=self.none_variable,
            command=lambda: self.super_toggle_none(True),
        )
        self.none_checkbox.grid(row=0, column=1)

        roles_list: list[str] = self.parent.file_manager.get_value(
            FILE.AGENT_CONFIG, "roles"
        )

        super_role_checkboxes_frame = ThemedFrame(self)
        super_role_checkboxes_frame.pack(fill=ctk.X, pady=(0, 10))

        self.role_variables = {role: ctk.BooleanVar(value=False) for role in roles_list}

        for col, role in enumerate(roles_list):
            super_role_checkboxes_frame.grid_columnconfigure(col, weight=1)

            role_color = self.theme[role]

            self.super_role_checkboxes[role] = ThemedCheckbox(
                super_role_checkboxes_frame,
                text=f"{role.capitalize()}s",
                text_color=BRIGHTEN_COLOR(role_color, 1.3),
                fg_color=role_color,
                hover_color=BRIGHTEN_COLOR(role_color, 1.1),
                variable=self.role_variables[role],
                command=lambda role=role: self.super_toggle_role(role, True),
            )
            self.super_role_checkboxes[role].grid(row=0, column=col, pady=10)

        agents_frame = ThemedFrame(self, fg_color="transparent")
        agents_frame.pack(fill=ctk.BOTH, expand=True, pady=(0, 10))

        always_true = ctk.BooleanVar(value=True)
        self.agent_checkboxes = {role: dict() for role in roles_list}
        for col, role in enumerate(roles_list):
            role_agents: list[str] = self.parent.file_manager.get_value(
                FILE.AGENT_CONFIG, role
            )
            agents_frame.grid_columnconfigure(col, weight=1)

            role_frame = ThemedFrame(agents_frame)
            padx = 0 if col == 0 else (5, 0)
            role_frame.grid(row=0, column=col, sticky=ctk.NSEW, padx=padx)
            role_color = self.theme[role]

            for row, agent_name in enumerate(role_agents):

                dependent_var = (
                    self.parent.agent_states[agent_name][0]
                    if len(self.parent.agent_states[agent_name]) != 1
                    else always_true
                )

                variable = (
                    self.parent.agent_states[agent_name][1]
                    if len(self.parent.agent_states[agent_name]) != 1
                    else self.parent.agent_states[agent_name][0]
                )

                self.agent_checkboxes[role][agent_name] = DependentCheckbox(
                    role_frame,
                    text=agent_name.capitalize(),
                    text_color=BRIGHTEN_COLOR(role_color, 1.3),
                    fg_color=role_color,
                    hover_color=BRIGHTEN_COLOR(role_color, 1.1),
                    variable=variable,
                    dependent_variable=dependent_var,
                    command=lambda: self.toggle_agent(True),
                )

                ypad = 5 if row == 0 else (0, 5)
                self.agent_checkboxes[role][agent_name].pack(pady=ypad)

        self.update_super_checkboxes()

    def on_raise(self):
        self.update_super_checkboxes()

    def super_toggle_all(self, update_super=False):
        for role in self.role_variables:
            self.role_variables[role].set(True)
            self.super_toggle_role(role)

        if update_super:
            self.update_super_checkboxes()

    def super_toggle_none(self, update_super=False):
        for role in self.role_variables:
            self.role_variables[role].set(False)
            self.super_toggle_role(role)

        if update_super:
            self.update_super_checkboxes()

    def super_toggle_role(self, role: str, update_super=False):
        value = self.role_variables[role].get()

        for agent in self.agent_checkboxes[role]:
            if not self.agent_checkboxes[role][agent].dependent_variable.get():
                continue

            self.agent_checkboxes[role][agent].variable.set(value)

        if update_super:
            self.update_super_checkboxes()

    def toggle_agent(self, update_super=False):
        if update_super:
            self.update_super_checkboxes()

    def update_super_checkboxes(self):

        agent_values = {}
        for role in self.agent_checkboxes:
            agent_values[role] = [
                self.agent_checkboxes[role][agent].variable.get()
                for agent in self.agent_checkboxes[role]
                if self.agent_checkboxes[role][agent].dependent_variable.get()
            ]

        for role, values in agent_values.items():
            if all(values):
                self.role_variables[role].set(True)
            else:
                self.role_variables[role].set(False)

        all_selected = all([all(role) for role in agent_values.values()])

        none_selected = all([not any(role) for role in agent_values.values()])

        self.all_variable.set(all_selected)
        self.none_variable.set(none_selected)

        match self.all_variable.get(), self.none_variable.get():
            case (True, False):
                self.all_checkbox.disable()
                self.none_checkbox.enable()
            case (False, True):
                self.all_checkbox.enable()
                self.none_checkbox.disable()
            case _:
                self.all_checkbox.enable()
                self.none_checkbox.enable()

        if not none_selected:
            self.parent.random_select_available.set(True)
        else:
            self.parent.random_select_available.set(False)


# endregion

# region: Save Files Frame


class SaveFilesFrame(SideFrame):
    parent: "VALocker"

    buttons: list[SaveButton]
    favorite_buttons: list[SaveButton] = []

    new_file_icon = ctk.CTkImage(Image.open(ICON.NEW_FILE.value), size=(20, 20))

    def __init__(self, parent: "VALocker"):
        super().__init__(parent)

        self.scrollable_frame = ThemedScrollableFrame(self, label_text="Save Files")
        self.scrollable_frame.pack(fill=ctk.BOTH, expand=True, pady=(10, 0))
        self.scrollable_frame.grid_columnconfigure(0, weight=1)

        self.generate_save_list(first_time=True)

        self.new_save_button = ThemedButton(
            self,
            text="",
            image=self.new_file_icon,
            width=40,
            command=self.new_save,
            fg_color=self.theme["foreground"],
            hover_color=self.theme["foreground-hover"],
        )
        self.new_save_button.pack(side=ctk.RIGHT, pady=(5, 10), padx=0)

    def generate_save_list(self, first_time=False) -> None:
        if not first_time:
            for button in self.buttons:
                button.destroy()

        favorite_button_names = [f"{button.save_name}.yaml" for button in self.favorite_buttons]
        if first_time:
            for favorited_save in self.parent.file_manager.get_value(
                FILE.SETTINGS, "favoritedSaveFiles"
            ):
                favorite_button_names.append(favorited_save)

        self.buttons = []
        self.favorite_buttons = []
        for save_name in self.parent.save_manager.get_all_save_files():
            button = SaveButton(self.scrollable_frame, save_file=save_name)
            if f"{button.save_name}.yaml" in favorite_button_names:
                button.toggle_favorite(value=True)
            self.buttons.append(button)

        self.reorder_buttons()
        self.change_selected(self.parent.current_save_name.get())

    def new_save(self) -> None:
        dialog = InputDialog(
            self.parent, title="New Save", label="Enter New Save Name:", placeholder="Save Name"
        )
        file_name = dialog.get_input()
        
        if file_name is None:
            return
                
        if file_name in self.parent.save_manager.get_all_save_files():
            self.parent.logger.error(f"Save '{file_name}' already exists.")
            return
        
        if file_name == "":
            self.parent.logger.error("Save name cannot be empty.")
            return
        
        file_name = file_name.strip() + ".yaml"
        
        self.parent.save_manager.create_new_save(file_name)
        self.parent.load_save(file_name, save_current_config=True)
        self.generate_save_list()

    def change_save(self, save_name: str) -> None:
        save_name += ".yaml"
        self.change_selected(save_name)
        self.parent.load_save(save_name, save_current_config=True)

    def change_selected(self, save_name: str) -> None:
        for button in self.buttons:
            if button.save_name == save_name:
                button.set_selected(True)
            else:
                button.set_selected(False)

    def favorite_button(self, button: SaveButton, reorderList=True) -> None:
        if button.favorited:
            self.favorite_buttons.append(button)
        else:
            self.favorite_buttons.remove(button)

        if reorderList:
            self.reorder_buttons()

        self.parent.file_manager.set_value(
            FILE.SETTINGS,
            "favoritedSaveFiles",
            [button.save_file for button in self.favorite_buttons],
        )

    def reorder_buttons(self) -> None:
        other_buttons = sorted(
            [button for button in self.buttons if not button.favorited],
            key=lambda button: button.save_name,
        )
        
        for index, button in enumerate(self.favorite_buttons + other_buttons):
            button.grid(row=index, column=0, pady=5, padx=5, sticky=ctk.EW)


# endregion

# region: Update Frame


class UpdateFrame(ctk.CTkFrame):
    default_config = {
        "fg_color": "background",
    }

    font_size: tuple[str, int]

    status_variables: dict[FILE, ctk.StringVar]
    version_variable: ctk.StringVar

    def __init__(self, parent: "VALocker", **kwargs):
        self.parent = parent
        self.theme = parent.theme

        config = {
            key: kwargs.get(key, parent.theme.get(value, value))
            for key, value in self.default_config.items()
        }
        config.update(kwargs)

        self.font_size = (self.theme["font"], 18)

        super().__init__(parent, **config)

        self.grid_columnconfigure(0, weight=1)

        self.update_label = ThemedLabel(
            self,
            text="Checking for Updates",
            font=(self.theme["font"], 20),
        )
        self.update_label.grid(row=0, column=0, sticky="nsew", padx=10, pady=(20, 5))

        self.progress_bar = ctk.CTkProgressBar(
            self,
            fg_color=self.theme["foreground"],
            border_color=self.theme["foreground-highlight"],
            progress_color=self.theme["accent"],
            border_width=1,
            mode="indeterminate",
            indeterminate_speed=2,
            width=300,
            height=10,
        )
        self.progress_bar.grid(row=1, column=0, pady=(0, 10))
        self.progress_bar.start()

        self.status_variables = {}

        for row, file_to_check in enumerate(self.parent.updater.FILES_TO_CHECK):
            row += 2

            file_frame = ThemedFrame(self)

            file_frame.grid(row=row, column=0, sticky=ctk.NSEW, padx=50, pady=10)

            file_name = file_to_check.name.split("_")
            file_name = " ".join([word.capitalize() for word in file_name])

            file_label = ThemedLabel(
                file_frame,
                text=file_name,
                font=self.font_size,
            )
            file_label.pack(side=ctk.LEFT, padx=10, pady=10)

            text_var = ctk.StringVar(value="Waiting")
            file_status = ThemedLabel(
                file_frame, textvariable=text_var, font=self.font_size
            )
            file_status.pack(side=ctk.RIGHT, padx=10, pady=10)

            self.status_variables[file_to_check] = text_var

        version_frame = ThemedFrame(self)
        version_frame.grid(row=row + 1, column=0, sticky=ctk.NSEW, padx=50, pady=10)

        version_label = ThemedLabel(version_frame, text="Version", font=self.font_size)
        version_label.pack(side=ctk.LEFT, padx=10, pady=10)

        self.version_variable = ctk.StringVar(value="Waiting")
        version_status = ThemedLabel(
            version_frame, textvariable=self.version_variable, font=self.font_size
        )
        version_status.pack(side=ctk.RIGHT, padx=10, pady=10)

    def finished_checking_updates(self):
        self.update_label.configure(text="Loading VALocker")


# endregion

# region: Tools Frame


class ToolsFrame(SideFrame):
    parent: "VALocker"

    # Status of tools thread
    tool_status: ctk.BooleanVar

    # Dict of tool button names and their corresponding button
    tool_buttons: dict[str, ThemedButton] = dict()

    def __init__(self, parent: "VALocker"):
        super().__init__(parent)

        tools: dict[str, ctk.BooleanVar] = {"Anti-AFK": self.parent.anti_afk}

        self.tool_status = self.parent.tools_thread_running

        toggle_tool_status = IndependentButton(
            self,
            text=["Tools: Enabled", "Tools: Disabled"],
            variable=self.tool_status,
            command=lambda: self.parent.toggle_boolean(self.tool_status),
            corner_radius=10,
        )
        toggle_tool_status.pack(side=ctk.TOP, fill=ctk.X, pady=10)

        scrollable_tools_frame = ThemedScrollableFrame(self)
        scrollable_tools_frame.pack(fill=ctk.BOTH, expand=True, pady=(0, 10))

        scrollable_tools_frame.columnconfigure(0, weight=1)

        # Scrollable frame items
        for index, tool in enumerate(tools):
            var = tools[tool]

            button = IndependentButton(
                scrollable_tools_frame,
                text=tool,
                variable=var,
                command=lambda tool=var: self.parent.toggle_boolean(tool),
            )
            button.grid(row=index, column=0, padx=10, pady=10, sticky=ctk.NSEW)

            self.tool_buttons[tool] = button


# endregion

# region: Popups


class ThemedPopup(ctk.CTkToplevel):
    default_config = {
        "fg_color": "foreground",
    }

    def __init__(self, parent: "VALocker", title, **kwargs):
        self.theme = parent.theme

        config = {
            key: kwargs.get(key, parent.theme.get(value, value))
            for key, value in self.default_config.items()
        }
        config.update(kwargs)

        super().__init__(**config)
        self.geometry("300x200")
        self.title = title


class InputDialog(ctk.CTkToplevel):
    """
    Modified version of the InputDialog class from the customtkinter library to use the active theme.
    See https://github.com/TomSchimansky/CustomTkinter for the original class.
    """
    
    default_config = {
        "fg_color": "background",
    }

    theme: dict[str, str]

    def __init__(self, parent: "VALocker", title: str, label: str, placeholder: str, prefill: str = None, **kwargs):

        self.theme = parent.theme

        config = {
            key: kwargs.get(key, parent.theme.get(value, value))
            for key, value in self.default_config.items()
        }
        config.update(kwargs)

        super().__init__(**config)

        self.user_input: Union[str, None] = None
        self.label = label
        self.placeholder = placeholder
        self.prefill = prefill

        self.title(title)
        self.lift()  # lift window on top
        self.attributes("-topmost", True)  # stay on top
        self.protocol("WM_DELETE_WINDOW", self._on_closing)
        self.after(
            10, self.create_widgets
        )  # create widgets with slight delay, to avoid white flickering of background
        self.resizable(False, False)
        self.grab_set()  # make other windows not clickable

    def create_widgets(self):
        self.grid_columnconfigure((0, 1), weight=1)
        self.rowconfigure(0, weight=1)

        self.label = ThemedLabel(
            self,
            width=300,
            wraplength=300,
            fg_color="transparent",
            text=self.label
        )
        self.label.grid(row=0, column=0, columnspan=2, padx=20, pady=20, sticky="ew")

        self.entry = ctk.CTkEntry(
            self,
            width=230,
            fg_color=self.theme["foreground"],
            text_color=self.theme["text"],
            font=self.theme["label"],
        )
        self.entry.grid(
            row=1, column=0, columnspan=2, padx=20, pady=(0, 20), sticky="ew"
        )
        
        if self.prefill:
            self.entry.insert(0, self.prefill)

        self.ok_button = ThemedButton(
            self,
            fg_color=self.theme["button-enabled"],
            hover_color=self.theme["button-enabled-hover"],
            text="Ok",
            command=self._ok_event,
        )
        self.ok_button.grid(
            row=2, column=1, columnspan=1, padx=(20, 10), pady=(0, 20), sticky="ew"
        )

        self.cancel_button = ThemedButton(
            self,
            fg_color=self.theme["button-disabled"],
            hover_color=self.theme["button-disabled-hover"],
            text="Cancel",
            command=self._cancel_event,
        )
        self.cancel_button.grid(
            row=2, column=0, columnspan=1, padx=(10, 20), pady=(0, 20), sticky="ew"
        )

        self.after(
            150, lambda: self.entry.focus()
        )  # set focus to entry with slight delay, otherwise it won't work
        self.entry.bind("<Return>", self._ok_event)
        self.entry.bind("<Escape>", self._cancel_event)

    def _ok_event(self, event=None):
        self.user_input = self.entry.get()
        self.grab_release()
        self.destroy()

    def _on_closing(self):
        self.grab_release()
        self.destroy()

    def _cancel_event(self):
        self.grab_release()
        self.destroy()

    def get_input(self):
        self.master.wait_window(self)
        return self.user_input


# endregion
