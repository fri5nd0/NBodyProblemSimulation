import numpy as np
import matplotlib
matplotlib.use("TkAgg")

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk

paused = True

dt = 0.1
skip = 50
time_per_frame = dt * skip 

#Change input txts here, add more etc.
#for more planets, add more txt files and load them here
#Then add the plotting code for them in the update function below.
#LOAD SYSTEM A DATA
p1a = np.loadtxt("planet11.txt")
p2a = np.loadtxt("planet21.txt")
p3a = np.loadtxt("planet31.txt")

#LOAD SYSTEM B DATA
p1b = np.loadtxt("planet12.txt")
p2b = np.loadtxt("planet22.txt")
p3b = np.loadtxt("planet32.txt")

#################################

x1a, y1a = p1a[:,0], p1a[:,1]
x2a, y2a = p2a[:,0], p2a[:,1]
x3a, y3a = p3a[:,0], p3a[:,1]

x1b, y1b = p1b[:,0], p1b[:,1]
x2b, y2b = p2b[:,0], p2b[:,1]
x3b, y3b = p3b[:,0], p3b[:,1]

x1a, y1a = x1a[::skip], y1a[::skip]
x2a, y2a = x2a[::skip], y2a[::skip]
x3a, y3a = x3a[::skip], y3a[::skip]

x1b, y1b = x1b[::skip], y1b[::skip]
x2b, y2b = x2b[::skip], y2b[::skip]
x3b, y3b = x3b[::skip], y3b[::skip]

frames = min(len(x1a), len(x1b))

root = tk.Tk()
root.title("Three-Body System Comparison")

def on_closing():
    root.quit()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_closing)


fig, ax = plt.subplots(figsize=(9,9))
ax.set_aspect("equal")
ax.grid(True)
ax.set_xlabel("X")
ax.set_ylabel("Y")
ax.set_title("Three-Body Comparison")

canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)


time_text = ax.text(
    0.02, 0.95,
    "",
    transform=ax.transAxes,
    fontsize=12,
    verticalalignment='top',
    bbox=dict(facecolor='white', alpha=0.8)
)

line1a, = ax.plot([], [], 'b-', label='Planet 1 (A)')
line2a, = ax.plot([], [], 'r-', label='Planet 2 (A)')
line3a, = ax.plot([], [], 'g-', label='Planet 3 (A)')
point1a, = ax.plot([], [], 'bo')
point2a, = ax.plot([], [], 'ro')
point3a, = ax.plot([], [], 'go')

# --- System B ---
line1b, = ax.plot([], [], 'b--', label='Planet 1 (B)')
line2b, = ax.plot([], [], 'r--', label='Planet 2 (B)')
line3b, = ax.plot([], [], 'g--', label='Planet 3 (B)')
point1b, = ax.plot([], [], 'bs')
point2b, = ax.plot([], [], 'rs')
point3b, = ax.plot([], [], 'gs')

ax.legend()

view_mode = tk.StringVar(value="Both")

def update_visibility():
    mode = view_mode.get()

    show_A = mode in ("A", "Both")
    show_B = mode in ("B", "Both")

    for obj in [line1a, line2a, line3a, point1a, point2a, point3a]:
        obj.set_visible(show_A)

    for obj in [line1b, line2b, line3b, point1b, point2b, point3b]:
        obj.set_visible(show_B)

    canvas.draw_idle()

def toggle_pause():
    global paused

    if paused:
        anim.event_source.start()
        pause_button.config(text="Pause")
        paused = False
    else:
        anim.event_source.stop()
        pause_button.config(text="Resume")
        paused = True


control_frame = tk.Frame(root)
control_frame.pack(side=tk.BOTTOM)

tk.Radiobutton(control_frame, text="System A", variable=view_mode,
               value="A", command=update_visibility).pack(side=tk.LEFT)

tk.Radiobutton(control_frame, text="System B", variable=view_mode,
               value="B", command=update_visibility).pack(side=tk.LEFT)

tk.Radiobutton(control_frame, text="Both", variable=view_mode,
               value="Both", command=update_visibility).pack(side=tk.LEFT)
pause_button = tk.Button(
    control_frame,
    text="Pause",
    command=toggle_pause
)
pause_button.pack(side=tk.LEFT, padx=10)

def update(frame):

    i = max(frame-1, 0)

    # Compute simulation time
    sim_time = frame * time_per_frame
    time_text.set_text(
        f"Time: {sim_time:,.1f} s   ({sim_time/3600:.2f} h)"
    )

    # Update trajectories
    line1a.set_data(x1a[:frame], y1a[:frame])
    line2a.set_data(x2a[:frame], y2a[:frame])
    line3a.set_data(x3a[:frame], y3a[:frame])

    line1b.set_data(x1b[:frame], y1b[:frame])
    line2b.set_data(x2b[:frame], y2b[:frame])
    line3b.set_data(x3b[:frame], y3b[:frame])

    # Update markers
    point1a.set_data([x1a[i]], [y1a[i]])
    point2a.set_data([x2a[i]], [y2a[i]])
    point3a.set_data([x3a[i]], [y3a[i]])

    point1b.set_data([x1b[i]], [y1b[i]])
    point2b.set_data([x2b[i]], [y2b[i]])
    point3b.set_data([x3b[i]], [y3b[i]])

    # Dynamic camera
    visible_positions = []

    if view_mode.get() in ("A", "Both"):
        visible_positions += [
            (x1a[i], y1a[i]),
            (x2a[i], y2a[i]),
            (x3a[i], y3a[i])
        ]

    if view_mode.get() in ("B", "Both"):
        visible_positions += [
            (x1b[i], y1b[i]),
            (x2b[i], y2b[i]),
            (x3b[i], y3b[i])
        ]

    if visible_positions:
        xs, ys = zip(*visible_positions)
        xs = np.array(xs)
        ys = np.array(ys)

        cx, cy = np.mean(xs), np.mean(ys)
        max_dist = max(np.max(np.abs(xs - cx)),
                       np.max(np.abs(ys - cy)))

        buffer = max_dist * 2.0 + 1e-5

        ax.set_xlim(cx - buffer, cx + buffer)
        ax.set_ylim(cy - buffer, cy + buffer)

    return []

# =========================
# START ANIMATION
# =========================

anim = FuncAnimation(
    fig,
    update,
    frames=frames,
    interval=20,
    blit=False
)


root.mainloop()
