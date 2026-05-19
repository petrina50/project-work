# -*- coding: utf-8 -*-
"""
Created on Fri May  8 09:40:29 2026

@author: HP
"""

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class BeamGeometry:
    
    
    def __init__(self):
        self.num_spans = 3  
        self.span_lengths = [5.0, 5.0, 5.0]  
        self.total_length = sum(self.span_lengths)
        
    def set_span_lengths(self, lengths):
        if len(lengths) != self.num_spans:
            raise ValueError(f"Expected {self.num_spans} spans")
        for i, L in enumerate(lengths):
            if L <= 0:
                raise ValueError(f"Span {i+1} length must be positive")
        self._lengths = lengths
        self.total_length = sum(lengths)
        return True
    
    def get_span_length(self, span_index):
        return self.span_lengths[span_index - 1]
    
    def get_coordinate(self, span, distance_in_span):
        coord = sum(self.span_lengths[:span-1]) + distance_in_span
        return coord
    
    def get_all_coordinates(self):
        coords = [0]
        for i in range(self.num_spans):
            coords.append(coords[-1] + self.span_lengths[i])
        return coords
    
    def display_geometry(self):
        info = f"""
BEAM GEOMETRY:
- Number of spans: {self.num_spans}
- Total length: {self.total_length} m
"""
        return info


class SupportConditions:
    PIN = 1      
    ROLLER = 2   
    FIXED = 3    
    
    def __init__(self):
        self.num_supports = 4
        self.support_types = [self.PIN]+ [self.ROLLER]* (self.num_supports-2) + [self.ROLLER]
        self.support_names = {self.PIN: "Pin", self.ROLLER: "Roller", self.FIXED: "Fixed"}
        
    def set_support_type(self, support_index, support_type):
        if support_index < 1 or support_index > self.num_supports:
            raise ValueError(f"Support index must be between 1 and {self.num_supports}")
        if support_type not in [self.PIN, self.ROLLER, self.FIXED]:
            raise ValueError("Wrong support type")
        self.support_types[support_index - 1] = support_type
        
    def get_support_type(self, support_index):
        return self.support_types[support_index - 1]
    
    
    def get_boundary_condition(self, support_index):
        if support_index == 1 or support_index == self.num_supports:
            if self.support_types[support_index - 1] == self.FIXED:
                return None  
            else:
                return 0.0    
        return None  
    
    def display_supports(self):
        info = "SUPPORT CONDITIONS:\n"
        for i in range(self.num_supports):
            support_letter = chr(65 + i)  
            info += f"  Support {support_letter}: {self.support_names[self.support_types[i]]}\n"
        return info


class LoadApplication:
    def __init__(self):
        self.point_loads = []        
        self.distributed_loads = []  
        self.moment_loads = []       
        
    def add_point_load(self, span, distance, magnitude):
        if span < 1 or span > 3:
            raise ValueError("Span must be 1, 2, or 3")
        if distance < 0:
            raise ValueError("Distance cannot be negative")
        if magnitude == 0:
            raise ValueError("Load magnitude cannot be zero")
        self.point_loads.append([span, distance, magnitude])  
        print(f"DEBUG: Point load added - span:{span}, dist:{distance}, force:{magnitude}")
        
    def add_distributed_load(self, span, start, end, magnitude):
        if span < 1 or span > 3:
            raise ValueError("Span must be 1, 2, or 3")
        if start >= end:
            raise ValueError("Start position must be less than end position")
        if start < 0:
            raise ValueError("Start position cannot be negative")
        if magnitude == 0:
            raise ValueError("Load magnitude cannot be zero")
        self.distributed_loads.append([span, start, end, magnitude])  
        print(f"DEBUG: UDL added - span:{span}, start:{start}, end:{end}, mag:{magnitude}")
        
    def add_moment_load(self, span, distance, magnitude):
        if span < 1 or span > 3:
            raise ValueError("Span must be 1, 2, or 3")
        if distance < 0:
            raise ValueError("Distance cannot be negative")
        if magnitude == 0:
            raise ValueError("Load magnitude cannot be zero")
        self.moment_loads.append([span, distance, magnitude])
        
    def remove_load(self, load_index, load_type):
        if load_type == "point":
            del self.point_loads[load_index]
        elif load_type == "distributed":
            del self.distributed_loads[load_index]
        elif load_type == "moment":
            del self.moment_loads[load_index]
            
    def clear_all_loads(self):
        self.point_loads.clear()
        self.distributed_loads.clear()
        self.moment_loads.clear()
        
    def get_total_load(self):
        total = 0
        for load in self.point_loads:
            total += abs(load[2])
        for load in self.distributed_loads:
            total += abs(load[3]) * (load[2] - load[1])
        return total
    
    def get_fixed_end_moments(self, span_length):

        pass
    
    def display_loads(self):
        info = "APPLIED LOADS:\n"
        if self.point_loads:
            info += "  Point Loads:\n"
            for i, load in enumerate(self.point_loads):
                info += f"    Point {i+1}: Span {load[0]}, {load[2]} kN at {load[1]} m\n"
        if self.distributed_loads:
            info += "  Distributed Loads:\n"
            for i, load in enumerate(self.distributed_loads):
                info += f"    UDL {i+1}: Span {load[0]}, {load[3]} kN/m from {load[1]} to {load[2]} m\n"
        if not (self.point_loads or self.distributed_loads):
            info += "  No loads applied\n"
        return info

class ThreeMomentSolver:
    def __init__(self, geometry, supports, loads):
        self.geometry = geometry
        self.supports = supports
        self.loads = loads
        self.support_moments = None
        self.fem_left = None
        self.fem_right = None
        
    def calculate_fixed_end_moments(self, span_index):
        L = self.geometry.get_span_length(span_index)
        FEM_left = 0.0
        FEM_right = 0.0
        
        for load in self.loads.point_loads: 
            if load[0] == span_index:
                a = load[1]
                b = L - a
                P = load[2]
                FEM_left += P * a * (b**2) / (L**2)
                FEM_right += P * (a**2) * b / (L**2)
        
    
        for load in self.loads.distributed_loads:  
            if load[0] == span_index:
                start = load[1]
                end = load[2]
                w = load[3]
                total_load = w * (end - start)
                center = start + (end - start) / 2
                a = start
                b = L - end
                FEM_left += (total_load * a * b*2) / (L*2)
                FEM_right += (total_load * a*2 * b) / (L*2)
                
        return FEM_left, FEM_right
    
    def build_three_moment_equations(self):
        n = self.geometry.num_spans
        m = n - 1
        
        if m == 0:
            return None, None
        
        A = np.zeros((m, m))
        B = np.zeros(m)
        
        self.fem_left = []
        self.fem_right = []
        for i in range(1, n + 1):
            FL, FR = self.calculate_fixed_end_moments(i)
            self.fem_left.append(FL)
            self.fem_right.append(FR)
        
        for i in range(m):
            L_left = self.geometry.get_span_length(i + 1)
            L_right = self.geometry.get_span_length(i + 2)
            
            if i > 0:
                A[i, i-1] = L_left
            A[i, i] = 2 * (L_left + L_right)
            if i < m - 1:
                A[i, i+1] = L_right
            
            B[i] = -6 * (self.fem_right[i] + self.fem_left[i + 1])
        
        return A, B
    
    def solve(self):
        A, B = self.build_three_moment_equations()
        
        if A is None:
            self.support_moments = [0.0] * (self.geometry.num_spans + 1)
            return self.support_moments
        
        try:
            interior_moments = np.linalg.solve(A, B)
            self.support_moments = [0.0] * (self.geometry.num_spans + 1)
            self.support_moments[0] = 0.0
            for i in range(len(interior_moments)):
                self.support_moments[i + 1] = interior_moments[i]
            self.support_moments[-1] = 0.0
            return self.support_moments
        except np.linalg.LinAlgError as e:
            raise Exception(f"Matrix singular: {e}")
    
    def display_results(self):
        if self.support_moments is None:
            return "Run solver first"
        info = "SUPPORT MOMENTS:\n"
        for i, M in enumerate(self.support_moments):
            support_letter = chr(65 + i)
            info += f"  M_{support_letter} = {M:.3f} kN·m\n"
        return info


class ShearForceCalculator:
    def __init__(self, geometry, supports, loads, moments):
        self.geometry = geometry
        self.supports = supports
        self.loads = loads
        self.moments = moments  
        self.reactions = None
        self.shear_force = None
        self.bending_moment = None
        
    def calculate_reactions(self):
        n_spans = self.geometry.num_spans
        n_supports = n_spans + 1
        reactions = [0.0] * n_supports
        
        for span in range(1, n_spans + 1):
            L = self.geometry.get_span_length(span)
            M_left = self.moments[span - 1]
            M_right = self.moments[span]
            total_load = 0
            moment_about_right = 0
            
            for load in self.loads.point_loads:
                if load[0] == span:
                    a = load[1]  
                    P = load[2]
                    total_load += P
                    moment_about_right += P * (L - a)
            
            for load in self.loads.distributed_loads:
                if load[0] == span:
                    start = load[1]
                    end = load[2]
                    w = load[3]
                    load_magnitude = w * (end - start)
                    centroid = start + (end - start) / 2
                    total_load += load_magnitude
                    moment_about_right += load_magnitude * (L - centroid)
            
            for load in self.loads.moment_loads:
                if load[0] == span:
                    M_applied = load[2]
                    moment_about_right += M_applied
            
            R_left = (moment_about_right + M_right - M_left) / L
            R_right = total_load - R_left
            
            reactions[span - 1] += R_left
            reactions[span] += R_right
        
        self.reactions = reactions
        return reactions
    
    def calculate_shear_force_distribution(self, num_points=200):
        if self.reactions is None:
            self.calculate_reactions()
            
        self.shear_force = {'x': [], 'V': []}
        self.bending_moment = {'x': [], 'M': []}
        
        cumulative_x = 0
        
        for span in range(1, self.geometry.num_spans + 1):
            L = self.geometry.get_span_length(span)
            x_points = np.linspace(0, L, num_points)
            M_left = self.moments[span - 1]
            R_left = self.reactions[span - 1]
            
            for x in x_points:
                global_x = cumulative_x + x
                V = R_left
                M = R_left * x + M_left
                
                for load in self.loads.point_loads:
                    if load[0] == span and x > load[1]:
                        P = load[2]
                        V -= P
                        M -= P * (x - load[1])
                
                for load in self.loads.distributed_loads:
                    if load[0] == span:
                        start = load[1]
                        end = load[2]
                        w = load[3]
                        if x > start:
                            loaded_length = min(x, end) - start
                            if loaded_length > 0:
                                centroid = start + loaded_length / 2
                                V -= w * loaded_length
                                M -= w * loaded_length * (x - centroid)
                
                for load in self.loads.moment_loads:
                    if load[0] == span and abs(x - load[1]) < 0.001:
                        M += load[2]
                
                self.shear_force['x'].append(global_x)
                self.shear_force['V'].append(V)
                self.bending_moment['x'].append(global_x)
                self.bending_moment['M'].append(M)
            
            cumulative_x += L
        
        return self.shear_force, self.bending_moment
    
    def display_reactions(self):
        if self.reactions is None:
            self.calculate_reactions()
        
        info = "SUPPORT REACTIONS:\n"
        for i, R in enumerate(self.reactions):
            support_letter = chr(65 + i)
            info += f"  R_{support_letter} = {R:.3f} kN\n"
        
        
        total_load = self.loads.get_total_load()
        total_reaction = sum(self.reactions)
        error = abs(total_load - total_reaction)
        info += f"\nEQUILIBRIUM CHECK:\n"
        info += f"  Total Load = {total_load:.3f} kN\n"
        info += f"  Total Reaction = {total_reaction:.3f} kN\n"
        info += f"  Error = {error:.6f} kN\n"
        
        return info


class PlottingModule:
    
    def __init__(self, geometry, shear_force, bending_moment):
        self.geometry = geometry
        self.shear_force = shear_force
        self.bending_moment = bending_moment
        
    def plot_diagrams(self):
        if not self.shear_force or not self.bending_moment:
            raise Exception("No data to plot")
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
        fig.suptitle('Continuous Beam Analysis Results', fontsize=14, fontweight='bold')
        x = self.shear_force['x']
        V = self.shear_force['V']
        
        ax1.plot(x, V, 'b-', linewidth=2, label='Shear Force')
        ax1.axhline(y=0, color='k', linewidth=0.5, linestyle='--')
        ax1.fill_between(x, 0, V, alpha=0.3, color='blue')
        ax1.set_ylabel('Shear Force (kN)', fontsize=12)
        ax1.set_title('Shear Force Diagram (SFD)', fontsize=12, fontweight='bold')
        ax1.grid(True, alpha=0.3)
        ax1.legend()
        
        
        support_x = self.geometry.get_all_coordinates()
        for x_sup in support_x:
            ax1.axvline(x=x_sup, color='red', linestyle=':', alpha=0.5)
        
        x = self.bending_moment['x']
        M = self.bending_moment['M']
        
        ax2.plot(x, M, 'r-', linewidth=2, label='Bending Moment')
        ax2.axhline(y=0, color='k', linewidth=0.5, linestyle='--')
        ax2.fill_between(x, 0, M, alpha=0.3, color='red')
        ax2.set_xlabel('Distance Along Beam (m)', fontsize=12)
        ax2.set_ylabel('Bending Moment (kN·m)', fontsize=12)
        ax2.set_title('Bending Moment Diagram (BMD)', fontsize=12, fontweight='bold')
        ax2.grid(True, alpha=0.3)
        ax2.legend()
        
        for x_sup in support_x:
            ax2.axvline(x=x_sup, color='red', linestyle=':', alpha=0.5)
        
        for i, x_sup in enumerate(support_x):
            support_letter = chr(65 + i)
            ax2.text(x_sup, min(M) * 0.9, f'   {support_letter}', fontsize=10, fontweight='bold')
        
        plt.tight_layout()
        plt.show()
    
    def embed_in_tkinter(self, parent_frame):
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 6))
        
        ax1.plot(self.shear_force['x'], self.shear_force['V'], 'b-', linewidth=2)
        ax1.axhline(y=0, color='k', linewidth=0.5)
        ax1.set_ylabel('Shear (kN)')
        ax1.set_title('SFD')
        ax1.grid(True, alpha=0.3)
        ax2.plot(self.bending_moment['x'], self.bending_moment['M'], 'r-', linewidth=2)
        ax2.axhline(y=0, color='k', linewidth=0.5)
        ax2.set_xlabel('Distance (m)')
        ax2.set_ylabel('Moment (kN·m)')
        ax2.set_title('BMD')
        ax2.grid(True, alpha=0.3)
        
        canvas = FigureCanvasTkAgg(fig, master=parent_frame)
        canvas.draw()
        return canvas.get_tk_widget()


class BeamAppGUI:
    
    def __init__(self, root):
        self.root = root
        self.root.title("Group 2 - Continuous Beam Solver")
        self.root.geometry("600x550")
        self.geometry = BeamGeometry()
        self.supports = SupportConditions()
        self.loads = LoadApplication()
        self.solver = None
        self.shear_calc = None
        self.plotter = None
        
        self.create_widgets()
        
    def create_widgets(self):
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True)
        
        self.create_geometry_tab(notebook)
        self.create_supports_tab(notebook)
        self.create_loads_tab(notebook)
        self.create_analysis_tab(notebook)
        self.create_diagrams_tab(notebook)
        self.status = tk.Label(self.root, text="Ready", bd=1, relief='sunken', anchor='w')
        self.status.pack(side='bottom', fill='x')
    
    def create_geometry_tab(self, notebook):
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="1. Beam Geometry")
        
        tk.Label(frame, text="Span Lengths (meters)", font=('Arial', 12, 'bold')).pack(pady=10)
        
        span_frame = tk.Frame(frame)
        span_frame.pack(pady=10)
        
        self.span_entries = []
        for i in range(3):
            tk.Label(span_frame, text=f"Span {i+1}:").grid(row=i, column=0, padx=5, pady=5)
            entry = tk.Entry(span_frame, width=15)
            entry.insert(0, " ")
            entry.grid(row=i, column=1, padx=5, pady=5)
            self.span_entries.append(entry)
        
        tk.Button(frame, text="Set Span Lengths", command=self.set_span_lengths,
                 bg='pink', font=('Arial', 10, 'bold')).pack(pady=10)
        
        self.geometry_text = tk.Text(frame, height=8, width=50)
        self.geometry_text.pack(pady=10)
        
    def create_supports_tab(self, notebook):
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="2. Support Conditions")
        
        tk.Label(frame, text="Support Types", font=('Arial', 12, 'bold')).pack(pady=10)
        
        self.support_vars = []
        support_frame = tk.Frame(frame)
        support_frame.pack(pady=10)
        
        supports = ['A (Left)', 'B (Interior 1)', 'C (Interior 2)', 'D (Right)']
        for i, support in enumerate(supports):
            tk.Label(support_frame, text=f"{support}:").grid(row=i, column=0, padx=5, pady=5)
            var = tk.StringVar(value="Roller")
            self.support_vars.append(var)
            combo = ttk.Combobox(support_frame, textvariable=var, values=['Pin', 'Roller', 'Fixed'], width=10)
            combo.grid(row=i, column=1, padx=5, pady=5)
            if i == 0:
                var.set("Pin")
            else:
                var.set("Roller")
        
        tk.Button(frame, text="Set Support Conditions", command=self.set_support_conditions,
                 bg='pink', font=('Arial', 10, 'bold')).pack(pady=10)
        
        self.supports_text = tk.Text(frame, height=8, width=50)
        self.supports_text.pack(pady=10)
    
    def create_loads_tab(self, notebook):
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="3. Load Application")
    
        group1 = tk.LabelFrame(frame, text="Add Point Load", font=('Arial', 10, 'bold'))
        group1.pack(fill='x', padx=10, pady=5)
        
        load_frame = tk.Frame(group1)
        load_frame.pack(pady=5)
        
        tk.Label(load_frame, text="Span (1-3):").grid(row=0, column=0, padx=5)
        self.pt_span = tk.Entry(load_frame, width=8)
        self.pt_span.grid(row=0, column=1, padx=5)
        
        tk.Label(load_frame, text="Distance (m):").grid(row=0, column=2, padx=5)
        self.pt_dist = tk.Entry(load_frame, width=8)
        self.pt_dist.grid(row=0, column=3, padx=5)
        
        tk.Label(load_frame, text="Force (kN):").grid(row=0, column=4, padx=5)
        self.pt_force = tk.Entry(load_frame, width=8)
        self.pt_force.grid(row=0, column=5, padx=5)
        
        tk.Button(load_frame, text="Add Point Load", command=self.add_point_load,
                 bg='pink').grid(row=0, column=6, padx=10)
        
        group2 = tk.LabelFrame(frame, text="Add Distributed Load (UDL)", font=('Arial', 10, 'bold'))
        group2.pack(fill='x', padx=10, pady=5)
        
        udl_frame = tk.Frame(group2)
        udl_frame.pack(pady=5)
        
        tk.Label(udl_frame, text="Span (1-3):").grid(row=0, column=0, padx=5)
        self.udl_span = tk.Entry(udl_frame, width=6)
        self.udl_span.grid(row=0, column=1, padx=5)
        
        tk.Label(udl_frame, text="Start (m):").grid(row=0, column=2, padx=5)
        self.udl_start = tk.Entry(udl_frame, width=6)
        self.udl_start.grid(row=0, column=3, padx=5)
        
        tk.Label(udl_frame, text="End (m):").grid(row=0, column=4, padx=5)
        self.udl_end = tk.Entry(udl_frame, width=6)
        self.udl_end.grid(row=0, column=5, padx=5)
        
        tk.Label(udl_frame, text="Mag (kN/m):").grid(row=0, column=6, padx=5)
        self.udl_mag = tk.Entry(udl_frame, width=6)
        self.udl_mag.grid(row=0, column=7, padx=5)
        
        tk.Button(udl_frame, text="Add UDL", command=self.add_distributed_load,
                 bg='pink').grid(row=0, column=8, padx=10)
        

        group3 = tk.LabelFrame(frame, text="Applied Loads", font=('Arial', 10, 'bold'))
        group3.pack(fill='both', expand=True, padx=10, pady=5)
        
        self.load_listbox = tk.Listbox(group3, height=6)
        self.load_listbox.pack(fill='both', expand=True, side='left')
        
        scroll = tk.Scrollbar(group3, orient='vertical', command=self.load_listbox.yview)
        scroll.pack(side='right', fill='y')
        self.load_listbox.config(yscrollcommand=scroll.set)
        
        btn_frame = tk.Frame(group3)
        btn_frame.pack(pady=5)
        tk.Button(btn_frame, text="Remove Selected", command=self.remove_load).pack(side='left', padx=5)
        tk.Button(btn_frame, text="Clear All", command=self.clear_loads).pack(side='left', padx=5)
    
    def create_analysis_tab(self, notebook):
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="4. Analysis Results")
        
        self.results_text = tk.Text(frame, wrap='word', height=20)
        self.results_text.pack(fill='both', expand=True, padx=10, pady=10)
        
        btn_frame = tk.Frame(frame)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="Run Analysis", command=self.run_analysis,
                 bg='pink', font=('Arial', 12, 'bold'), width=15).pack(side='left', padx=10)
    
    def create_diagrams_tab(self, notebook):
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="5. Diagrams")
        
        self.plot_frame = tk.Frame(frame)
        self.plot_frame.pack(fill='both', expand=True)
        
        btn_frame = tk.Frame(frame)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="Generate Diagrams", command=self.generate_diagrams,
                 bg='pink', font=('Arial', 10, 'bold'), width=15).pack()
    

    
    def set_span_lengths(self):
        try:
            lengths = [float(entry.get()) for entry in self.span_entries]
            self.geometry.set_span_lengths(lengths)
            self.geometry_text.delete(1.0, tk.END)
            self.geometry_text.insert(1.0, self.geometry.display_geometry())
            self.status.config(text=f"Geometry updated: spans = {lengths} m")
            messagebox.showinfo("Saved", "Span lengths updated!")
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid input: {e}")
    
    def set_support_conditions(self):
        type_map = {"Pin": SupportConditions.PIN,
                   "Roller": SupportConditions.ROLLER,
                   "Fixed": SupportConditions.FIXED}
        
        for i, var in enumerate(self.support_vars):
            support_type = type_map[var.get()]
            self.supports.set_support_type(i + 1, support_type)
        
        self.supports_text.delete(1.0, tk.END)
        self.supports_text.insert(1.0, self.supports.display_supports())
        self.status.config(text="Support conditions updated")
        messagebox.showinfo("Good", "Support conditions set!")
    
    def add_point_load(self):
        try:
            span = int(self.pt_span.get())
            dist = float(self.pt_dist.get())
            force = float(self.pt_force.get())
            
            self.loads.add_point_load(span, dist, force)
            self.update_load_display()
            self.status.config(text=f"Point load added: {force} kN at {dist} m in span {span}")
            
            self.pt_span.delete(0, tk.END)
            self.pt_dist.delete(0, tk.END)
            self.pt_force.delete(0, tk.END)
        except ValueError as e:
            messagebox.showerror("Error", str(e))
    
    def add_distributed_load(self):
        try:
            span = int(self.udl_span.get())
            start = float(self.udl_start.get())
            end = float(self.udl_end.get())
            mag = float(self.udl_mag.get())
            
            self.loads.add_distributed_load(span, start, end, mag)
            self.update_load_display()
            self.status.config(text=f"UDL added: {mag} kN/m from {start} to {end} m in span {span}")
            self.udl_span.delete(0, tk.END)
            self.udl_start.delete(0, tk.END)
            self.udl_end.delete(0, tk.END)
            self.udl_mag.delete(0, tk.END)
        except ValueError as e:
            messagebox.showerror("Error", str(e))
    
    def update_load_display(self):
        self.load_listbox.delete(0, tk.END)
        
        for load in self.loads.point_loads:
            self.load_listbox.insert(tk.END, f"Point: Span {load[0]}, {load[2]} kN at {load[1]} m")
        
        for load in self.loads.distributed_loads:
            self.load_listbox.insert(tk.END, f"UDL: Span {load[0]}, {load[3]} kN/m, {load[1]}-{load[2]} m")
    
    def remove_load(self):
        selection = self.load_listbox.curselection()
        if selection:
            idx = selection[0]
            if idx < len(self.loads.point_loads):
                del self.loads.point_loads[idx]
            else:
                del self.loads.distributed_loads[idx - len(self.loads.point_loads)]
            self.update_load_display()
            self.status.config(text="Load removed")
    
    def clear_loads(self):
        self.loads.clear_all_loads()
        self.update_load_display()
        self.status.config(text="All loads cleared")
    
    def run_analysis(self):
        try:
            self.status.config(text="Running three-moment solver...")
            self.solver = ThreeMomentSolver(self.geometry, self.supports, self.loads)
            moments = self.solver.solve()
            self.status.config(text="Calculating shear forces and reactions...")
            self.shear_calc = ShearForceCalculator(self.geometry, self.supports, self.loads, moments)
            reactions = self.shear_calc.calculate_reactions()
            self.shear_calc.calculate_shear_force_distribution()
            
            
            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(1.0, "="*60 + "\n")
            self.results_text.insert(1.0, "CONTINUOUS BEAM SOLVER RESULTS\n")
            self.results_text.insert(1.0, "="*60 + "\n\n")
            
            self.results_text.insert(1.0, self.geometry.display_geometry())
            self.results_text.insert(1.0, "\n")
            self.results_text.insert(1.0, self.supports.display_supports())
            self.results_text.insert(1.0, "\n")
            self.results_text.insert(1.0, self.loads.display_loads())
            self.results_text.insert(1.0, "\n")
            self.results_text.insert(1.0, self.solver.display_results())
            self.results_text.insert(1.0, "\n")
            self.results_text.insert(1.0, self.shear_calc.display_reactions())
            
            self.status.config(text="Analysis complete!")
            messagebox.showinfo("Analysis Complete", "Beam analysis completed successfully!")
            
        except Exception as e:
            messagebox.showerror("Analysis Error", f"Error during analysis: {str(e)}")
            self.status.config(text="Analysis failed")
    
    def generate_diagrams(self):
        if self.shear_calc is None or self.shear_calc.shear_force is None:
            messagebox.showwarning("No Analysis", "Please run analysis first!")
            return
        
        try:
            self.plotter = PlottingModule(self.geometry, self.shear_calc.shear_force, 
                                         self.shear_calc.bending_moment)
            
            for widget in self.plot_frame.winfo_children():
                widget.destroy()
            
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6))
            
            x = self.shear_calc.shear_force['x']
            V = self.shear_calc.shear_force['V']
            ax1.plot(x, V, 'b-', linewidth=2)
            ax1.axhline(y=0, color='k', linewidth=0.5, linestyle='--')
            ax1.fill_between(x, 0, V, alpha=0.3, color='blue')
            ax1.set_ylabel('Shear Force (kN)')
            ax1.set_title('Shear Force Diagram (SFD)')
            ax1.grid(True, alpha=0.3)
            

            M = self.shear_calc.bending_moment['M']
            ax2.plot(x, M, 'r-', linewidth=2)
            ax2.axhline(y=0, color='k', linewidth=0.5, linestyle='--')
            ax2.fill_between(x, 0, M, alpha=0.3, color='red')
            ax2.set_xlabel('Distance Along Beam (m)')
            ax2.set_ylabel('Bending Moment (kN·m)')
            ax2.set_title('Bending Moment Diagram (BMD)')
            ax2.grid(True, alpha=0.3)
           
            
            support_x = self.geometry.get_all_coordinates()
            for x_sup in support_x:
                ax1.axvline(x=x_sup, color='red', linestyle=':', alpha=0.5)
                ax2.axvline(x=x_sup, color='red', linestyle=':', alpha=0.5)
            
           
            canvas = FigureCanvasTkAgg(fig, master=self.plot_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill='both', expand=True)
            
            self.status.config(text="Diagrams generated successfully!")
            
        except Exception as e:
            messagebox.showerror("Plot Error", f"Error generating diagrams: {str(e)}")



if __name__ == "__main__":
    root = tk.Tk()
    app = BeamAppGUI(root)
    root.mainloop()