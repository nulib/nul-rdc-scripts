# Many thanks to Code First with Hala on Youtube for her video Tkinter Data Entry Form tutorial for beginners - Python GUI project [responsive layout]
import os
import openpyxl
import tkinter as tkin
from tkinter import scrolledtext, messagebox
from nulrdcscripts.tools.errortool.params import args


def main():
    window = tkin.Tk()
    window.title("Error Entry Form")

    frame = tkin.Frame(window)
    frame.pack()

    def enter_data():

        video_id = video_id_entry.get()
        video_title = video_title_entry.get()
        project_id = project_id_entry.get()

        if video_id and video_title and project_id:
            runtime = run_time_entry.get()
            audiobuzz = audiobuzz_check_var.get()
            audiocrackle = audiocrackle_check_var.get()
            audiodistortion = audiodistortion_check_var.get()
            audiodrop = audiodrop_check_var.get()
            audiomuffled = audiomuffled_check_var.get()
            audionoise = audionoise_check_var.get()
            bearding = bearding_check_var.get()
            carrierleak = carrier_leak_check_var.get()
            colorsmear = color_smearing_check_var.get()
            creased = creased_check_var.get()
            chromnoise = chromnoise_check_var.get()
            crosstalk = crosstalk_check_var.get()
            crushed = crushed_check_var.get()
            dihedralmal = dihedral_check_var.get()
            dotcrawl = dotcrawl_check_var.get()
            dropouts = dropouts_check_var.get()
            egli = egli_check_var.get()
            fluorescentstrobe = fluorescent_check_var.get()
            ghosting = ghost_check_var.get()
            headclogging = headclog_check_var.get()
            hHold = horiHold_check_var.get()
            hueError = hueError_check_var.get()
            humTrouble = hum_check_var.get()
            incTVStand = incomp_TVStand_var.get()
            incFam = incomp_inFam_var.get()
            expanshrink = expanshrink_check_var.get()
            longPlay = longPlay_check_var.get()
            lossColor = losscolor_check_var.get()
            moire = moire_check_var.get()
            scratchwear = scratchwear_check_var.get()
            shiftedheadswitch = shiftheadswitch_check_var.get()
            skew = skew_check_var.get()
            stickyshed = stick_check_var.get()
            stiction = stiction_check_var.get()
            scpe = scpe_check_var.get()
            tapeDeform = deform_check_var.get()
            tapeMisalign = misalign_check_var.get()
            quilting = quilting_check_var.get()
            ringing = ringing_check_var.get()
            tBCError = tBCError_check_var.get()
            tracking = track_check_var.get()
            vgae = vgae_check_var.get()
            ycdelay = ycdelay_check_var.get()
            ven = ven_check_var.get()
            vhold = vhold_check_var.get()
            vPictJump = vPictJump_check_var.get()
            vsync = vsync_check_var.get()
            visibleFrame = visibleFrameLine_check_var.get()
            additionalNotes = notes_entry.get("1.0", tkin.END)

            video_errors = [
                audiobuzz,
                audiocrackle,
                audiodrop,
                audiodistortion,
                audiomuffled,
                audionoise,
                bearding,
                carrierleak,
                colorsmear,
                creased,
                chromnoise,
                crosstalk,
                crushed,
                dihedralmal,
                dotcrawl,
                dropouts,
                egli,
                fluorescentstrobe,
                ghosting,
                headclogging,
                hHold,
                hueError,
                humTrouble,
                incTVStand,
                incFam,
                expanshrink,
                longPlay,
                lossColor,
                moire,
                scratchwear,
                shiftedheadswitch,
                skew,
                stickyshed,
                stiction,
                scpe,
                tapeDeform,
                tapeMisalign,
                quilting,
                ringing,
                tBCError,
                tracking,
                vgae,
                ycdelay,
                ven,
                vhold,
                vPictJump,
                vsync,
                visibleFrame,
                additionalNotes,
            ]
            errors = "; ".join([x for x in video_errors if x != "Absent"])

            file_output = os.path.abspath(args.output_path)
            xlsx_file = os.path.abspath((file_output + "/" + project_id + ".xlsx"))
            if not os.path.exists(xlsx_file): # if there is no is no xlsx file already named this 
                wb=openpyxl.Workbook()
                sheet=wb.active
                heading=["Project ID","Video ID","Video Title","Run Time (Mins)", "Log"]
                sheet.append(heading)
                wb.save(xlsx_file)
            wb=openpyxl.load_workbook(xlsx_file)
            sheet=wb.active
            sheet.append([project_id,video_id,video_title,runtime,errors])
            wb.save(xlsx_file)

            
        else:
            tkin.messagebox.showwarning(
                title="Error",
                message="You have not entered a project id, a video id, and/or a video title. Please re-enter data.",
            )

    # Saving video Information

    # Setting up labels
    video_info_frame = tkin.LabelFrame(
        frame, text="Video Information", padx=20, pady=20
    )
    video_info_frame.pack(fill=tkin.BOTH, expand=True)
    video_title = tkin.Label(video_info_frame, text="Video Title")
    video_title.grid(row=0, column=0)
    video_id = tkin.Label(video_info_frame, text="Video Identifier")
    video_id.grid(row=0, column=1)
    project_id = tkin.Label(video_info_frame, text="Project ID")
    project_id.grid(row=0, column=2)
    run_time = tkin.Label(video_info_frame, text="Runtime (Mins)")
    run_time.grid(row=0, column=3)

    # Setting up entry boxes

    video_title_entry = tkin.Entry(video_info_frame)
    video_id_entry = tkin.Entry(video_info_frame)
    project_id_entry = tkin.Entry(video_info_frame)
    run_time_entry = tkin.Spinbox(video_info_frame, from_="0", to="500")
    video_title_entry.grid(row=1, column=0)
    video_id_entry.grid(row=1, column=1)
    project_id_entry.grid(row=1, column=2)
    run_time_entry.grid(row=1, column=3)

    for widget in video_info_frame.winfo_children():
        widget.grid_configure(padx=10, pady=5)

    # Saving video errors
    errors_frame = tkin.LabelFrame(frame, text="Errors Present", padx=20, pady=20)
    errors_frame.pack(fill=tkin.BOTH, expand=True)
    audiobuzz_check_var = tkin.StringVar(value="Absent")
    audiobuzz_check = tkin.Checkbutton(
        errors_frame,
        text="Audio Buzz/Hum",
        variable=audiobuzz_check_var,
        onvalue="Audio Buzz/Hum",
        offvalue="Absent",
    )
    audiocrackle_check_var = tkin.StringVar(value="Absent")
    audiocrackle_check = tkin.Checkbutton(
        errors_frame,
        text="Audio Crackle",
        variable=audiocrackle_check_var,
        onvalue="Audio Crackle",
        offvalue="Absent",
    )
    audiodistortion_check_var = tkin.StringVar(value="Absent")
    audiodistortion_check = tkin.Checkbutton(
        errors_frame,
        text="Audio Distortion",
        variable=audiodistortion_check_var,
        onvalue="Audio Distortion",
        offvalue="Absent",
    )
    audiodrop_check_var = tkin.StringVar(value="Absent")
    audiodrop_check = tkin.Checkbutton(
        errors_frame,
        text="Audio Dropout",
        variable=audiodrop_check_var,
        onvalue="Audio Dropout",
        offvalue="Absent",
    )
    audiomuffled_check_var = tkin.StringVar(value="Absent")
    audiomuffled_check = tkin.Checkbutton(
        errors_frame,
        text="Audio Muffled",
        variable=audiomuffled_check_var,
        onvalue="Audio Muffled",
        offvalue="Absent",
    )
    audionoise_check_var = tkin.StringVar(value="Absent")
    audionoise_check = tkin.Checkbutton(
        errors_frame,
        text="Audio Noise",
        variable=audionoise_check_var,
        onvalue="Audio Noise",
        offvalue="Absent",
    )
    bearding_check_var = tkin.StringVar(value="Absent")
    bearding_check = tkin.Checkbutton(
        errors_frame,
        text="Bearding",
        variable=bearding_check_var,
        onvalue="Bearding",
        offvalue="Absent",
    )
    carrier_leak_check_var = tkin.StringVar(value="Absent")
    carrier_leak_check = tkin.Checkbutton(
        errors_frame,
        text="Carrier Leak",
        variable=carrier_leak_check_var,
        onvalue="Carrier Leak",
        offvalue="Absent",
    )
    color_smearing_check_var = tkin.StringVar(value="Absent")
    color_smearing_check = tkin.Checkbutton(
        errors_frame,
        text="Color Smearing",
        variable=color_smearing_check_var,
        onvalue="Color Smearing",
        offvalue="Absent",
    )
    creased_check_var = tkin.StringVar(value="Absent")
    creased_check = tkin.Checkbutton(
        errors_frame,
        text="Creased or Crumpled Tape",
        variable=creased_check_var,
        onvalue="Creased or Crumpled Tape",
        offvalue="Absent",
    )
    chromnoise_check_var = tkin.StringVar(value="Absent")
    chromnoise_check = tkin.Checkbutton(
        errors_frame,
        text="Chrominance Noise",
        variable=chromnoise_check_var,
        onvalue="Chrominance Noise",
        offvalue="Absent",
    )
    crosstalk_check_var = tkin.StringVar(value="Absent")
    crosstalk_check = tkin.Checkbutton(
        errors_frame,
        text="Crosstalk",
        variable=crosstalk_check_var,
        onvalue="Crosstalk",
        offvalue="Absent",
    )
    crushed_check_var = tkin.StringVar(value="Absent")
    crushed_check = tkin.Checkbutton(
        errors_frame,
        text="Chrushed Setup",
        variable=crushed_check_var,
        onvalue="Crushed Setup",
        offvalue="Absent",
    )
    dihedral_check_var = tkin.StringVar(value="Absent")
    dihedral_check = tkin.Checkbutton(
        errors_frame,
        text="Dihedral Maladjustment",
        variable=dihedral_check_var,
        onvalue="Dihedral Maladjustment",
        offvalue="Absent",
    )
    dotcrawl_check_var = tkin.StringVar(value="Absent")
    dotcrawl_check = tkin.Checkbutton(
        errors_frame,
        text="Dot Crawl",
        variable=dotcrawl_check_var,
        onvalue="Dot Crawl",
        offvalue="Absent",
    )
    dropouts_check_var = tkin.StringVar(value="Absent")
    dropouts_check = tkin.Checkbutton(
        errors_frame,
        text="Dropouts and Dropout Compensation",
        variable=dropouts_check_var,
        onvalue="Dropouts & Dropout Compensation",
        offvalue="Absent",
    )
    egli_check_var = tkin.StringVar(value="Absent")
    egli_check = tkin.Checkbutton(
        errors_frame,
        text="Electrical Ground Loop Interference",
        variable=egli_check_var,
        onvalue="Electrical Ground Loop Interference",
        offvalue="Absent",
    )
    fluorescent_check_var = tkin.StringVar(value="Absent")
    fluorescent_check = tkin.Checkbutton(
        errors_frame,
        text="Fluorescent Strobing",
        variable=fluorescent_check_var,
        onvalue="Fluorescent Strobing",
        offvalue="Absent",
    )
    ghost_check_var = tkin.StringVar(value="Absent")
    ghost_check = tkin.Checkbutton(
        errors_frame,
        text="Ghosting",
        variable=ghost_check_var,
        onvalue="Ghosting",
        offvalue="Absent",
    )
    headclog_check_var = tkin.StringVar(value="Absent")
    headclog_check = tkin.Checkbutton(
        errors_frame,
        text="Headclogging",
        variable=headclog_check_var,
        onvalue="Headclogging",
        offvalue="Absent",
    )
    horiHold_check_var = tkin.StringVar(value="Absent")
    horiHold_check = tkin.Checkbutton(
        errors_frame,
        text="Horizontal Hold",
        variable=horiHold_check_var,
        onvalue="Horizontal Hold",
        offvalue="Absent",
    )
    hueError_check_var = tkin.StringVar(value="Absent")
    hueError_check = tkin.Checkbutton(
        errors_frame,
        text="Hue Error NTSC",
        variable=hueError_check_var,
        onvalue="Hue Error",
        offvalue="Absent",
    )
    hum_check_var = tkin.StringVar(value="Absent")
    hum_check = tkin.Checkbutton(
        errors_frame,
        text="Hum Trouble",
        variable=hum_check_var,
        onvalue="Hum Trouble",
        offvalue="Absent",
    )
    incomp_TVStand_var = tkin.StringVar(value="Absent")
    incomp_TVStand = tkin.Checkbutton(
        errors_frame,
        text="Incompatibility TV Standards",
        variable=incomp_TVStand_var,
        onvalue="Incompatibility in TV Standards",
        offvalue="Absent",
    )
    incomp_inFam_var = tkin.StringVar(value="Absent")
    incomp_inFam = tkin.Checkbutton(
        errors_frame,
        text="Incompatibility in family of formats",
        variable=incomp_inFam_var,
        onvalue="Incompatibility in Family of Formats",
        offvalue="Absent",
    )
    expanshrink_check_var = tkin.StringVar(value="Absent")
    expanshrink_check = tkin.Checkbutton(
        errors_frame,
        text="Tape Expansion or Shrinkage",
        variable=expanshrink_check_var,
        onvalue="Tape Expansion or Shrinkage",
        offvalue="Absent",
    )
    longPlay_check_var = tkin.StringVar(value="Absent")
    longPlay_check = tkin.Checkbutton(
        errors_frame,
        text="Long Play",
        variable=longPlay_check_var,
        onvalue="Long Play",
        offvalue="Absent",
    )
    losscolor_check_var = tkin.StringVar(value="Absent")
    losscolor_check = tkin.Checkbutton(
        errors_frame,
        text="Loss of Color Lock",
        variable=losscolor_check_var,
        onvalue="Loss of Color Lock",
        offvalue="Absent",
    )
    moire_check_var = tkin.StringVar(value="Absent")
    moire_check = tkin.Checkbutton(
        errors_frame,
        text="Moire Effect",
        variable=moire_check_var,
        onvalue="Moire Effect",
        offvalue="Absent",
    )
    scratchwear_check_var = tkin.StringVar(value="Absent")
    scratchwear_check = tkin.Checkbutton(
        errors_frame,
        text="Scratches and Tape Wear",
        variable=scratchwear_check_var,
        onvalue="Scratches and Tape Wear",
        offvalue="Absent",
    )
    shiftheadswitch_check_var = tkin.StringVar(value="Absent")
    shiftheadswitch_check = tkin.Checkbutton(
        errors_frame,
        text="Shifted Head Switching Point",
        variable=shiftheadswitch_check_var,
        onvalue="Headswitching Noise",
        offvalue="Absent",
    )
    skew_check_var = tkin.StringVar(value="Absent")
    skew_check = tkin.Checkbutton(
        errors_frame,
        text="Skew Error",
        variable=skew_check_var,
        onvalue="Skew Error",
        offvalue="Absent",
    )
    stick_check_var = tkin.StringVar(value="Absent")
    stick_check = tkin.Checkbutton(
        errors_frame,
        text="Sticky Tape Syndrome",
        variable=stick_check_var,
        onvalue="Sticky Tape Syndrome",
        offvalue="Absent",
    )
    stiction_check_var = tkin.StringVar(value="Absent")
    stiction_check = tkin.Checkbutton(
        errors_frame,
        text="Stiction",
        variable=stiction_check_var,
        onvalue="Stiction",
        offvalue="Absent",
    )
    scpe_check_var = tkin.StringVar(value="Absent")
    scpe_check = tkin.Checkbutton(
        errors_frame,
        text="Subcarrier Phase Error",
        variable=scpe_check_var,
        onvalue="Subcarrier Phase Error",
        offvalue="Absent",
    )
    deform_check_var = tkin.StringVar(value="Absent")
    deform_check = tkin.Checkbutton(
        errors_frame,
        text="Tape Deformation",
        variable=deform_check_var,
        onvalue="Tape Deformation",
        offvalue="Absent",
    )
    misalign_check_var = tkin.StringVar(value="Absent")
    misalign_check = tkin.Checkbutton(
        errors_frame,
        text="Tape Misalignment",
        variable=misalign_check_var,
        onvalue="Tape Misalignment",
        offvalue="Absent",
    )
    quilting_check_var = tkin.StringVar(value="Absent")
    quilting_check = tkin.Checkbutton(
        errors_frame,
        text="Quilting",
        variable=quilting_check_var,
        onvalue="Quilting",
        offvalue="Absent",
    )
    ringing_check_var = tkin.StringVar(value="Absent")
    ringing_check = tkin.Checkbutton(
        errors_frame,
        text="Ringing",
        variable=ringing_check_var,
        onvalue="Ringing",
        offvalue="Absent",
    )
    tBCError_check_var = tkin.StringVar(value="Absent")
    tBCError_check = tkin.Checkbutton(
        errors_frame,
        text="TBC Error",
        variable=tBCError_check_var,
        onvalue="TBC Error",
        offvalue="Absent",
    )
    track_check_var = tkin.StringVar(value="Absent")
    track_check = tkin.Checkbutton(
        errors_frame,
        text="Tracking Error",
        variable=track_check_var,
        onvalue="Tracking Error",
        offvalue="Absent",
    )
    vgae_check_var = tkin.StringVar(value="Absent")
    vgae_check = tkin.Checkbutton(
        errors_frame,
        text="Vacuum Guide Adjustment Error",
        variable=vgae_check_var,
        onvalue="Vacuum Guide Adjustment Error",
        offvalue="Absent",
    )
    ycdelay_check_var = tkin.StringVar(value="Absent")
    ycdelay_check = tkin.Checkbutton(
        errors_frame,
        text="Y/C Delay Error",
        variable=ycdelay_check_var,
        onvalue="Y/C Delay Error",
        offvalue="Absent",
    )
    ven_check_var = tkin.StringVar(value="Absent")
    ven_check = tkin.Checkbutton(
        errors_frame,
        text="Venetian-Blind Effect PAL",
        variable=ven_check_var,
        onvalue="Venetian-Blind Effect",
        offvalue="Absent",
    )
    vhold_check_var = tkin.StringVar(value="Absent")
    vhold_check = tkin.Checkbutton(
        errors_frame,
        text="Vertical Hold",
        variable=vhold_check_var,
        onvalue="Vertical Hold",
        offvalue="Absent",
    )
    vPictJump_check_var = tkin.StringVar(value="Absent")
    vPictJump_check = tkin.Checkbutton(
        errors_frame,
        text="Vertical Picture Jumping",
        variable=vPictJump_check_var,
        onvalue="Vertical Picture Jumping",
        offvalue="Absent",
    )
    vsync_check_var = tkin.StringVar(value="Absent")
    vsync_check = tkin.Checkbutton(
        errors_frame,
        text="Vertical Synchronization Error",
        variable=vsync_check_var,
        onvalue="VSync Error",
        offvalue="Absent",
    )
    visibleFrameLine_check_var = tkin.StringVar(value="Absent")
    visibleFrameLine_check = tkin.Checkbutton(
        errors_frame,
        text="Visible Frame Line",
        variable=visibleFrameLine_check_var,
        onvalue="Visible Frame Line",
        offvalue="Absent",
    )

    audiobuzz_check.grid(row=1, column=0)
    audiocrackle_check.grid(row=2, column=0)
    audiodistortion_check.grid(row=3, column=0)
    audiodrop_check.grid(row=4, column=0)
    audiomuffled_check.grid(row=5, column=0)
    audionoise_check.grid(row=6, column=0)
    bearding_check.grid(row=7, column=0)
    carrier_leak_check.grid(row=8, column=0)
    color_smearing_check.grid(row=9, column=0)
    creased_check.grid(row=10, column=0)
    chromnoise_check.grid(row=11, column=0)
    crosstalk_check.grid(row=12, column=0)
    crushed_check.grid(row=1, column=1)
    dihedral_check.grid(row=2, column=1)
    dotcrawl_check.grid(row=3, column=1)
    dropouts_check.grid(row=4, column=1)
    egli_check.grid(row=5, column=1)
    fluorescent_check.grid(row=6, column=1)
    ghost_check.grid(row=7, column=1)
    headclog_check.grid(row=8, column=1)
    horiHold_check.grid(row=9, column=1)
    hueError_check.grid(row=10, column=1)
    hum_check.grid(row=11, column=1)
    incomp_TVStand.grid(row=12, column=1)
    incomp_inFam.grid(row=1, column=2)
    expanshrink_check.grid(row=2, column=2)
    longPlay_check.grid(row=3, column=2)
    losscolor_check.grid(row=4, column=2)
    moire_check.grid(row=5, column=2)
    scratchwear_check.grid(row=6, column=2)
    shiftheadswitch_check.grid(row=7, column=2)
    skew_check.grid(row=8, column=2)
    stick_check.grid(row=9, column=2)
    stiction_check.grid(row=10, column=2)
    scpe_check.grid(row=11, column=2)
    deform_check.grid(row=12, column=2)
    misalign_check.grid(row=1, column=3)
    quilting_check.grid(row=2, column=3)
    ringing_check.grid(row=3, column=3)
    tBCError_check.grid(row=4, column=3)
    track_check.grid(row=5, column=3)
    vgae_check.grid(row=6, column=3)
    ycdelay_check.grid(row=7, column=3)
    ven_check.grid(row=8, column=3)
    vhold_check.grid(row=9, column=3)
    vPictJump_check.grid(row=10, column=3)
    vsync_check.grid(row=11, column=3)
    visibleFrameLine_check.grid(row=12, column=3)

    for widget in errors_frame.winfo_children():
        widget.grid_configure(padx=10, pady=5, sticky="NW")

    # Setting up freeform entry

    notes_entry_frame = tkin.LabelFrame(
        frame, text=" Additional Notes", padx=20, pady=20
    )
    notes_entry_frame.pack(fill=tkin.BOTH, expand=True)
    notes_entry = tkin.scrolledtext.ScrolledText(notes_entry_frame)
    notes_entry.pack(fill=tkin.BOTH, expand=True)

    # Button setup
    submit_button = tkin.Button(
        frame, text="Submit Error Report", padx=20, pady=20, command=enter_data
    )
    submit_button.pack(fill="x", padx=10, pady=10)

    # Reset Button
    def reset_form():
        project_id_entry.delete(0, tkin.END)
        video_id_entry.delete(0, tkin.END)
        video_title_entry.delete(0, tkin.END)
        run_time_entry.delete(0, tkin.END)
        audiobuzz_check.deselect()
        audiocrackle_check.deselect()
        audiodistortion_check.deselect()
        audiodrop_check.deselect()
        audiomuffled_check.deselect()
        audionoise_check.deselect()
        bearding_check.deselect()
        carrier_leak_check.deselect()
        color_smearing_check.deselect()
        creased_check.deselect()
        chromnoise_check.deselect()
        crosstalk_check.deselect()
        crushed_check.deselect()
        dihedral_check.deselect()
        dotcrawl_check.deselect()
        dropouts_check.deselect()
        egli_check.deselect()
        ghost_check.deselect()
        headclog_check.deselect()
        horiHold_check.deselect()
        hueError_check.deselect()
        hum_check.deselect()
        incomp_TVStand.deselect()
        incomp_inFam.deselect()
        expanshrink_check.deselect()
        longPlay_check.deselect()
        losscolor_check.deselect()
        moire_check.deselect()
        scratchwear_check.deselect()
        shiftheadswitch_check.deselect()
        skew_check.deselect()
        stick_check.deselect()
        stiction_check.deselect()
        scpe_check.deselect()
        deform_check.deselect()
        misalign_check.deselect()
        quilting_check.deselect()
        ringing_check.deselect()
        tBCError_check.deselect()
        track_check.deselect()
        vgae_check.deselect()
        ycdelay_check.deselect()
        ven_check.deselect()
        vhold_check.deselect()
        vPictJump_check.deselect()
        vsync_check.deselect()
        visibleFrameLine_check.deselect()
        notes_entry.delete(1.0, tkin.END)

    reset_button = tkin.Button(
        frame, text="Reset Form", padx=20, pady=20, command=reset_form
    )
    reset_button.pack(fill="x", padx=10, pady=10)

    window.mainloop()


if __name__ == "__main__":
    main()
