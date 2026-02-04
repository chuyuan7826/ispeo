import matplotlib.pyplot as plt
import pandas as pd
from typing import Optional

def plot_simulation(df: pd.DataFrame, output_path: str, exp_data: Optional[pd.DataFrame] = None):
    """
    Generates a comprehensive plot of fermentation dynamics in a 2x2 grid.
    If exp_data is provided, overlays it as scatter points.
    """
    fig, axes = plt.subplots(2, 2, figsize=(14, 10), sharex=True)
    
    # Top Left: Biomass (X)
    ax1 = axes[0, 0]
    ax1.plot(df['time'], df['X'], label='Biomass (X) [Sim]', color='tab:blue', linewidth=2)
    if exp_data is not None:
        ax1.scatter(exp_data['time'], exp_data['X'], label='Biomass (X) [Exp]', color='tab:blue', marker='o')
    ax1.set_ylabel('Concentration [g/L]')
    ax1.set_title('Biomass Growth')
    ax1.legend()
    ax1.grid(True, linestyle='--', alpha=0.6)
    
    # Bottom Left: Products (P, B)
    ax2 = axes[1, 0]
    ax2.plot(df['time'], df['P'], label='Product (P) [Sim]', color='tab:red', linewidth=2)
    ax2.plot(df['time'], df['B'], label='By-product (B) [Sim]', color='tab:purple', linewidth=2)
    if exp_data is not None:
        ax2.scatter(exp_data['time'], exp_data['P'], label='Product (P) [Exp]', color='tab:red', marker='o')
        ax2.scatter(exp_data['time'], exp_data['B'], label='By-product (B) [Exp]', color='tab:purple', marker='x')
    ax2.set_ylabel('Concentration [g/L]')
    ax2.set_xlabel('Time [h]')
    ax2.set_title('Product Formation')
    ax2.legend()
    ax2.grid(True, linestyle='--', alpha=0.6)
    
    # Top Right: Substrate (S)
    ax3 = axes[0, 1]
    ax3.plot(df['time'], df['S'], label='Substrate (S) [Sim]', color='tab:orange', linewidth=2)
    if exp_data is not None:
        ax3.scatter(exp_data['time'], exp_data['S'], label='Substrate (S) [Exp]', color='tab:orange', marker='o')
    ax3.set_ylabel('Concentration [g/L]')
    ax3.set_title('Substrate Consumption')
    ax3.legend()
    ax3.grid(True, linestyle='--', alpha=0.6)
    
    # Bottom Right: Volume (V)
    ax4 = axes[1, 1]
    ax4.plot(df['time'], df['V'], label='Volume (V) [Sim]', color='tab:green', linewidth=2)
    if exp_data is not None:
        ax4.scatter(exp_data['time'], exp_data['V'], label='Volume (V) [Exp]', color='tab:green', marker='o')
    ax4.set_ylabel('Volume [L]')
    ax4.set_xlabel('Time [h]')
    ax4.set_title('Fermentation Volume')
    ax4.legend()
    ax4.grid(True, linestyle='--', alpha=0.6)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()

def plot_optimization_comparison(base_df: pd.DataFrame, opt_df: pd.DataFrame, output_path: str):
    """
    Generates a 2x2 grid comparing Baseline vs Optimized strategies.
    Baseline: Dashed lines, Lighter colors.
    Optimized: Solid lines, Vibrant colors.
    """
    fig, axes = plt.subplots(2, 2, figsize=(14, 10), sharex=True)
    
    # Helper for consistent plotting
    def plot_var(ax, var, label_name, color):
        ax.plot(base_df['time'], base_df[var], label=f'{label_name} (Base)', color=color, linestyle='--', alpha=0.6, linewidth=2)
        ax.plot(opt_df['time'], opt_df[var], label=f'{label_name} (Opt)', color=color, linestyle='-', linewidth=2)
        ax.grid(True, linestyle='--', alpha=0.6)
        ax.legend()

    # Top Left: Biomass (X)
    plot_var(axes[0, 0], 'X', 'Biomass', 'tab:blue')
    axes[0, 0].set_ylabel('Concentration [g/L]')
    axes[0, 0].set_title('Biomass Growth')

    # Bottom Left: Products (P, B)
    # P
    ax2 = axes[1, 0]
    ax2.plot(base_df['time'], base_df['P'], label='Product (Base)', color='tab:red', linestyle='--', alpha=0.6, linewidth=2)
    ax2.plot(opt_df['time'], opt_df['P'], label='Product (Opt)', color='tab:red', linestyle='-', linewidth=2)
    # B
    ax2.plot(base_df['time'], base_df['B'], label='By-product (Base)', color='tab:purple', linestyle='--', alpha=0.6, linewidth=2)
    ax2.plot(opt_df['time'], opt_df['B'], label='By-product (Opt)', color='tab:purple', linestyle='-', linewidth=2)
    ax2.set_ylabel('Concentration [g/L]')
    ax2.set_xlabel('Time [h]')
    ax2.set_title('Product Formation')
    ax2.legend()
    ax2.grid(True, linestyle='--', alpha=0.6)

    # Top Right: Substrate (S)
    plot_var(axes[0, 1], 'S', 'Substrate', 'tab:orange')
    axes[0, 1].set_ylabel('Concentration [g/L]')
    axes[0, 1].set_title('Substrate Consumption')

    # Bottom Right: Volume (V)
    plot_var(axes[1, 1], 'V', 'Volume', 'tab:green')
    axes[1, 1].set_ylabel('Volume [L]')
    axes[1, 1].set_xlabel('Time [h]')
    axes[1, 1].set_title('Fermentation Volume')

    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()