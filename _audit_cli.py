from samsung_mdc import MDC

cmds = sorted(MDC._commands.keys())
print(f"Total commands in lib: {len(cmds)}")

# Check field types
field_types = {}
for cname, cmd in MDC._commands.items():
    for f in getattr(cmd, "DATA", []):
        t = type(f).__name__
        enum = getattr(f, "enum", None)
        range_ = getattr(f, "range", None)
        multiple = getattr(f, "multiple", None)
        key = t
        if enum:     key += "+enum"
        if range_:   key += "+range"
        if multiple: key += "+multiple"
        field_types[key] = field_types.get(key, 0) + 1

print("\nField type distribution:")
for k, v in sorted(field_types.items()):
    print(f"  {k}: {v}")

# Per-command field details for commands with non-enum fields
print("\nCommands with non-enum fields (need manual entry — check placeholders):")
for cname in cmds:
    cmd = MDC._commands[cname]
    fields = getattr(cmd, "DATA", [])
    non_enum = []
    for f in fields:
        enum = getattr(f, "enum", None)
        if not enum:
            fname = getattr(f, "name", "?")
            t = type(f).__name__
            range_ = getattr(f, "range", None)
            multiple = getattr(f, "multiple", None)
            hint = t
            if range_:   hint += f" range={range_}"
            if multiple: hint += " multi"
            non_enum.append(f"{fname}({hint})")
    if non_enum:
        print(f"  {cname}: {', '.join(non_enum)}")

# Diff against README list
readme_cmds = set("""status video rgb serial_number error_status software_version
model_number power volume mute input_source picture_aspect screen_mode screen_size
network_configuration network_mode network_ap_config weekly_restart magicinfo_channel
magicinfo_server magicinfo_content_orientation mdc_connection contrast brightness
sharpness color tint h_position v_position auto_power clear_menu ir_state
rgb_contrast rgb_brightness auto_adjustment_on color_tone color_temperature standby
auto_lamp manual_lamp inverse video_wall_mode safety_lock panel_lock channel_change
volume_change ticker device_name osd picture_mode sound_mode all_keys_lock
panel_on_time video_wall_state video_wall_model model_name energy_saving reset
osd_type timer_13 timer_15 clock_m holiday_set holiday_get virtual_remote
network_standby dst auto_id_setting display_id clock_s set_content_download
launcher_play_via launcher_url_address osd_menu_orientation
osd_source_content_orientation osd_aspect_ratio osd_pip_orientation osd_menu_size
auto_source_switch auto_source panel screen_mute script raw""".split())

lib_cmds = set(cmds)
missing = readme_cmds - lib_cmds
extra   = lib_cmds - readme_cmds
print(f"\nIn README but missing from lib ({len(missing)}): {sorted(missing) or 'none'}")
print(f"In lib but not in README ({len(extra)}): {sorted(extra) or 'none'}")
print(f"\nAll 84 README commands present: {readme_cmds <= lib_cmds | {'script','raw'}}")
