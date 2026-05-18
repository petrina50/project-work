# -*- coding: utf-8 -*-
"""
Created on Mon May 11 06:32:52 2026

@author: user
"""

# -*- coding: utf-8 -*-
"""
Created on Fri May  8 00:32:55 2026

@author: HP
"""

import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import matplotlib.pyplot as plt


class BeamApp:
    def __init__(self, root):
        self.root = root
        self.root.title("A 3-Moment Beam Continuous  Analyzer")
        self.root.geometry("700x700")
        
        self.L = [5.0, 5.0, 5.0]  
        self.point_loads = []       
        self.udl_loads = []          
        
        self.create_widgets()
        
       
        for i, e in enumerate(self.entries):
            e.delete(0, tk.END)
            e.insert(0, " ")
    
    def create_widgets(self):
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True)
        
        input_frame = ttk.Frame(notebook)
        notebook.add(input_frame, text="Input Data")
        
        group1 = tk.LabelFrame(input_frame, text="Span Lengths (meters)")
        group1.pack(fill='x', padx=10, pady=5)
        
        self.entries = []
        for i in range(3):
            tk.Label(group1, text=f"Span {i+1}:").grid(row=i, column=0, padx=5, pady=5)
            e = tk.Entry(group1, width=15)
            e.grid(row=i, column=1, padx=5, pady=5)
            self.entries.append(e)
        
        tk.Button(group1, text="Set Lengths", command=self.set_lengths).grid(row=3, column=0, columnspan=2, pady=5)
        
        group2 = tk.LabelFrame(input_frame, text="Add Point Load")
        group2.pack(fill='x', padx=10, pady=5)
        
        tk.Label(group2, text="Span (1-3):").grid(row=0, column=0, padx=5, pady=5)
        self.span_entry = tk.Entry(group2, width=10)
        self.span_entry.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(group2, text="Distance (m):").grid(row=1, column=0, padx=5, pady=5)
        self.dist_entry = tk.Entry(group2, width=10)
        self.dist_entry.grid(row=1, column=1, padx=5, pady=5)
        
        tk.Label(group2, text="Force (kN):").grid(row=2, column=0, padx=5, pady=5)
        self.force_entry = tk.Entry(group2, width=10)
        self.force_entry.grid(row=2, column=1, padx=5, pady=5)
        
        tk.Button(group2, text="Add Point Load", command=self.add_point_load).grid(row=3, column=0, columnspan=2, pady=5)
        
        group3 = tk.LabelFrame(input_frame, text="Add Uniformly Distributed Load (UDL)")
        group3.pack(fill='x', padx=10, pady=5)
        
        tk.Label(group3, text="Span (1-3):").grid(row=0, column=0, padx=5, pady=5)
        self.udl_span_entry = tk.Entry(group3, width=10)
        self.udl_span_entry.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(group3, text="Start (m):").grid(row=1, column=0, padx=5, pady=5)
        self.udl_start_entry = tk.Entry(group3, width=10)
        self.udl_start_entry.grid(row=1, column=1, padx=5, pady=5)
        
        tk.Label(group3, text="End (m):").grid(row=2, column=0, padx=5, pady=5)
        self.udl_end_entry = tk.Entry(group3, width=10)
        self.udl_end_entry.grid(row=2, column=1, padx=5, pady=5)
        
        tk.Label(group3, text="Magnitude (kN/m):").grid(row=3, column=0, padx=5, pady=5)
        self.udl_mag_entry = tk.Entry(group3, width=10)
        self.udl_mag_entry.grid(row=3, column=1, padx=5, pady=5)
        
        tk.Button(group3, text="Add UDL", command=self.add_udl).grid(row=4, column=0, columnspan=2, pady=5)
        
        
        group4 = tk.LabelFrame(input_frame, text="Applied Loads")
        group4.pack(fill='both', expand=True, padx=10, pady=5)
        
        self.load_listbox = tk.Listbox(group4, height=6)
        self.load_listbox.pack(fill='both', expand=True, side='left')
        
        scroll = tk.Scrollbar(group4, orient='vertical', command=self.load_listbox.yview)
        scroll.pack(side='right', fill='y')
        self.load_listbox.config(yscrollcommand=scroll.set)
        
        btn_frame = tk.Frame(group4)
        btn_frame.pack(pady=5)
        tk.Button(btn_frame, text="Remove Selected", command=self.remove_load).pack(side='left', padx=5)
        tk.Button(btn_frame, text="Clear All Loads", command=self.clear_loads).pack(side='left', padx=5)
        
       
        results_frame = ttk.Frame(notebook)
        notebook.add(results_frame, text="Results")
        
        self.result_text = tk.Text(results_frame, wrap='word', height=15)
        self.result_text.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Buttons
        btn_frame2 = tk.Frame(results_frame)
        btn_frame2.pack(pady=10)
        tk.Button(btn_frame2, text="Run Analysis", command=self.analyze, bg='lightgreen', width=15).pack(side='left', padx=5)
        tk.Button(btn_frame2, text="Plot Diagrams", command=self.plot, bg='lightblue', width=15).pack(side='left', padx=5)
        
        
        self.status = tk.Label(self.root, text="Ready", bd=1, relief='sunken', anchor='w')
        self.status.pack(side='bottom', fill='x')
    
    def set_lengths(self):
        try:
            new_lengths = []
            for i, e in enumerate(self.entries):
                val = float(e.get())
                if val <= 0:
                    raise ValueError(f"Span {i+1} must be positive")
                new_lengths.append(val)
            self.L = new_lengths
            self.status.config(text=f"Spans set: {self.L[0]}, {self.L[1]}, {self.L[2]} meters")
            messagebox.showinfo("Success", f"Span lengths set to {self.L}")
        except ValueError as e:
            messagebox.showerror("Error", str(e))
        except:
            messagebox.showerror("Error", "Please enter valid numbers for all spans")
    
    def add_point_load(self):
        if any(l <= 0 for l in self.L):
            messagebox.showerror("Error", "Please set span lengths first")
            return
        
        try:
            span = int(self.span_entry.get().strip())
            dist = float(self.dist_entry.get().strip())
            force = float(self.force_entry.get().strip())
            
            if span < 1 or span > 3:
                raise ValueError("Span must be 1, 2, or 3")
            if dist < 0 or dist > self.L[span-1]:
                raise ValueError(f"Distance must be between 0 and {self.L[span-1]}")
            
            self.point_loads.append([span, dist, force])
            self.update_load_list()
            
            # Clear entries
            self.span_entry.delete(0, tk.END)
            self.dist_entry.delete(0, tk.END)
            self.force_entry.delete(0, tk.END)
            
            self.status.config(text=f"Point load added. Total: {len(self.point_loads) + len(self.udl_loads)} loads")
            
        except ValueError as e:
            messagebox.showerror("Error", str(e))
    
    def add_udl(self):
        """Add a uniformly distributed load"""
        if any(l <= 0 for l in self.L):
            messagebox.showerror("Error", "Please set span lengths first")
            return
        
        try:
            span = int(self.udl_span_entry.get().strip())
            start = float(self.udl_start_entry.get().strip())
            end = float(self.udl_end_entry.get().strip())
            mag = float(self.udl_mag_entry.get().strip())
            
            if span < 1 or span > 3:
                raise ValueError("Span must be 1, 2, or 3")
            if start < 0 or start > self.L[span-1]:
                raise ValueError(f"Start must be between 0 and {self.L[span-1]}")
            if end < 0 or end > self.L[span-1]:
                raise ValueError(f"End must be between 0 and {self.L[span-1]}")
            if start >= end:
                raise ValueError("End must be greater than start")
            
            self.udl_loads.append([span, start, end, mag])
            self.update_load_list()
            
            # Clear entries
            self.udl_span_entry.delete(0, tk.END)
            self.udl_start_entry.delete(0, tk.END)
            self.udl_end_entry.delete(0, tk.END)
            self.udl_mag_entry.delete(0, tk.END)
            
            self.status.config(text=f"UDL added. Total: {len(self.point_loads) + len(self.udl_loads)} loads")
            
        except ValueError as e:
            messagebox.showerror("Error", str(e))
    
    def update_load_list(self):
        """Update the listbox display"""
        self.load_listbox.delete(0, tk.END)
        
        for load in self.point_loads:
            self.load_listbox.insert(tk.END, f"Point - Span {load[0]}: {load[2]} kN at {load[1]} m")
        
        for load in self.udl_loads:
            self.load_listbox.insert(tk.END, f"UDL - Span {load[0]}: {load[3]} kN/m from {load[1]} to {load[2]} m")
    
    def remove_load(self):
        sel = self.load_listbox.curselection()
        if sel:
            idx = sel[0]
            if idx < len(self.point_loads):
                del self.point_loads[idx]
            else:
                del self.udl_loads[idx - len(self.point_loads)]
            self.update_load_list()
            self.status.config(text=f"Load removed. Total: {len(self.point_loads) + len(self.udl_loads)} loads")
    
    def clear_loads(self):
        if self.point_loads or self.udl_loads:
            self.point_loads.clear()
            self.udl_loads.clear()
            self.update_load_list()
            self.status.config(text="All loads cleared")
    
    def analyze(self):
        if any(l <= 0 for l in self.L):
            messagebox.showerror("Error", "Please set span lengths first")
            return
        
        L1, L2, L3 = self.L
        
        
        FEM_left = [0, 0, 0]
        FEM_right = [0, 0, 0]
        
        
        for span, dist, force in self.point_loads:
            L = self.L[span-1]
            a = dist
            b = L - a
            fem_left = force * a * (b*2) / (L*2)
            fem_right = force * (a*2) * b / (L*2)
            FEM_left[span-1] += fem_left
            FEM_right[span-1] += fem_right
        
        
        for span, start, end, mag in self.udl_loads:
            L = self.L[span-1]
            total_load = mag * (end - start)
            center = start + (end - start) / 2
            a = center
            b = L - a
            fem_left = total_load * a * (b*2) / (L*2)
            fem_right = total_load * (a*2) * b / (L*2)
            FEM_left[span-1] += fem_left
            FEM_right[span-1] += fem_right
        
       
        A = np.array([
            [2*(L1 + L2), L2],
            [L2, 2*(L2 + L3)]
        ])
        
        RHS = np.array([
            -6 * (FEM_right[0] + FEM_left[1]),
            -6 * (FEM_right[1] + FEM_left[2])
        ])
        
        try:
            M_BC = np.linalg.solve(A, RHS)
            M_B = M_BC[0]
            M_C = M_BC[1]
            M_A = 0.0
            M_D = 0.0
            
            moments = [M_A, M_B, M_C, M_D]
            
          
            reactions = self.calc_reactions(moments)
            
           
            self.last_moments = moments
            self.last_reactions = reactions
            
            
            self.show_results(moments, reactions)
            self.status.config(text="Analysis completed successfully")
            
        except np.linalg.LinAlgError:
            messagebox.showerror("Error", "Matrix is singular")
        except Exception as e:
            messagebox.showerror("Error", f"Analysis failed: {str(e)}")
    
    def calc_reactions(self, M):
        """Calculate support reactions"""
        L1, L2, L3 = self.L
        MA, MB, MC, MD = M
        R = [0.0, 0.0, 0.0, 0.0]
        
        for span in range(1, 4):
            L = self.L[span-1]
            total_load = 0
            moment_sum = 0
            
           
            for load in self.point_loads:
                if load[0] == span:
                    dist = load[1]
                    force = load[2]
                    total_load += force
                    moment_sum += force * (L - dist)
            
           
            for load in self.udl_loads:
                if load[0] == span:
                    start, end, mag = load[1], load[2], load[3]
                    load_amount = mag * (end - start)
                    center = start + (end - start) / 2
                    total_load += load_amount
                    moment_sum += load_amount * (L - center)
            
            R_left = moment_sum / L
            R_right = total_load - R_left
            
            if span == 1:
                R[0] = R_left + (MA - MB) / L
                R[1] = R_right - (MA - MB) / L
            elif span == 2:
                R[1] += R_left + (MB - MC) / L
                R[2] = R_right - (MB - MC) / L
            else:  # span == 3
                R[2] += R_left + (MC - MD) / L
                R[3] = R_right - (MC - MD) / L
        
        return R
    
    def show_results(self, moments, reactions):
        self.result_text.delete(1.0, tk.END)
        
        self.result_text.insert(tk.END, "="*55 + "\n")
        self.result_text.insert(tk.END, "BEAM ANALYSIS RESULTS\n")
        self.result_text.insert(tk.END, "="*55 + "\n\n")
        
        self.result_text.insert(tk.END, f"Span Lengths:\n")
        self.result_text.insert(tk.END, f"  L1 = {self.L[0]:.3f} m\n")
        self.result_text.insert(tk.END, f"  L2 = {self.L[1]:.3f} m\n")
        self.result_text.insert(tk.END, f"  L3 = {self.L[2]:.3f} m\n\n")
        
        self.result_text.insert(tk.END, f"Support Moments (kN·m):\n")
        self.result_text.insert(tk.END, f"  M_A = {moments[0]:.3f}\n")
        self.result_text.insert(tk.END, f"  M_B = {moments[1]:.3f}\n")
        self.result_text.insert(tk.END, f"  M_C = {moments[2]:.3f}\n")
        self.result_text.insert(tk.END, f"  M_D = {moments[3]:.3f}\n\n")
        
        self.result_text.insert(tk.END, f"Support Reactions (kN):\n")
        self.result_text.insert(tk.END, f"  R_A = {reactions[0]:.3f}\n")
        self.result_text.insert(tk.END, f"  R_B = {reactions[1]:.3f}\n")
        self.result_text.insert(tk.END, f"  R_C = {reactions[2]:.3f}\n")
        self.result_text.insert(tk.END, f"  R_D = {reactions[3]:.3f}\n\n")
        
       
        total_load = 0
        for load in self.point_loads:
            total_load += load[2]
        for load in self.udl_loads:
            total_load += load[3] * (load[2] - load[1])
        
        total_reaction = sum(reactions)
        self.result_text.insert(tk.END, f"Equilibrium Check:\n")
        self.result_text.insert(tk.END, f"  Total Load = {total_load:.3f} kN\n")
        self.result_text.insert(tk.END, f"  Total Reaction = {total_reaction:.3f} kN\n")
        self.result_text.insert(tk.END, f"  Error = {abs(total_load - total_reaction):.6f} kN\n")
    
    def plot(self):
        """Plot shear and moment diagrams"""
        if not hasattr(self, 'last_moments'):
            messagebox.showwarning("Warning", "Please run analysis first")
            return
        
        L1, L2, L3 = self.L
        M = self.last_moments
        R = self.last_reactions
        
        x_coords = []
        shear_values = []
        moment_values = []
        cumulative_x = 0
        
        for span in [1, 2, 3]:
            L = self.L[span-1]
            span_point_loads = [load for load in self.point_loads if load[0] == span]
            span_udls = [load for load in self.udl_loads if load[0] == span]
            
            points = np.linspace(0, L, 200)
            
            for x in points:
                x_pos = cumulative_x + x
                x_coords.append(x_pos)
                
                # Shear force
                V = R[span-1]
                for load in span_point_loads:
                    if x > load[1]:
                        V -= load[2]
                for load in span_udls:
                    start, end, mag = load[1], load[2], load[3]
                    if x > start:
                        length = min(x, end) - start
                        if length > 0:
                            V -= mag * length
                shear_values.append(V)
                
                
                M_x = R[span-1] * x + M[span-1]
                for load in span_point_loads:
                    if x > load[1]:
                        M_x -= load[2] * (x - load[1])
                for load in span_udls:
                    start, end, mag = load[1], load[2], load[3]
                    if x > start:
                        length = min(x, end) - start
                        if length > 0:
                            center = start + length / 2
                            M_x -= mag * length * (x - center)
                moment_values.append(M_x)
            
            cumulative_x += L
        
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
        
        ax1.plot(x_coords, shear_values, 'b-', linewidth=2)
        ax1.axhline(y=0, color='k', linewidth=0.5)
        ax1.fill_between(x_coords, 0, shear_values, alpha=0.2, color='blue')
        ax1.set_title('Shear Force Diagram', fontsize=12, fontweight='bold')
        ax1.set_ylabel('Shear Force (kN)', fontsize=10)
        ax1.grid(True, alpha=0.3)
        
        ax2.plot(x_coords, moment_values, 'r-', linewidth=2)
        ax2.axhline(y=0, color='k', linewidth=0.5)
        ax2.fill_between(x_coords, 0, moment_values, alpha=0.2, color='red')
        ax2.set_title('Bending Moment Diagram', fontsize=12, fontweight='bold')
        ax2.set_xlabel('Distance Along Beam (m)', fontsize=10)
        ax2.set_ylabel('Bending Moment (kN·m)', fontsize=10)
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()




if __name__ == "__main__":

  root = tk.Tk()
  app = BeamApp(root)
  root.mainloop()