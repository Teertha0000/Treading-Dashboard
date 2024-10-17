# Create two functions to calculate if a level is SUPPORT or a RESISTANCE level through fractal identification
def is_support_level(df, i):
    support = df['Low'][i] < df['Low'][i - 1] < df['Low'][i - 2] and df['Low'][i] < df['Low'][i + 1] < df['Low'][i + 2]
    return support


def is_resistance_level(df, i):
    resistance = df['High'][i] > df['High'][i - 1] > df['High'][i - 2] and df['High'][i] > df['High'][i + 1] > df['High'][i + 2]
    return resistance


# Function to identify support and resistance levels
def identify_levels(df):
    levels = []
    for i in range(2, df.shape[0] - 2):
        if is_support_level(df, i):
            levels.append((i, df['Low'][i], 'Support'))
        elif is_resistance_level(df, i):
            levels.append((i, df['High'][i], 'Resistance'))
    return levels


# Function to group levels within a certain price difference
def group_levels(levels, threshold=0.15):
    grouped_levels = []
    levels_sorted = sorted(levels, key=lambda x: x[1])

    current_group = []
    for level in levels_sorted:
        if not current_group or (level[1] - current_group[-1][1]) <= threshold:
            current_group.append(level)
        else:
            avg_price = sum(l[1] for l in current_group) / len(current_group)
            types = set(l[2] for l in current_group)
            type_label = '-'.join(sorted(types))
            grouped_levels.append((current_group[0][0], avg_price, type_label))
            current_group = [level]

    if current_group:
        avg_price = sum(l[1] for l in current_group) / len(current_group)
        types = set(l[2] for l in current_group)
        type_label = '-'.join(sorted(types))
        grouped_levels.append((current_group[0][0], avg_price, type_label))

    return grouped_levels


# Function to plot support and resistance levels on a Plotly figure
def plot_levels(fig, df, levels):
    for level in levels:
        fig.add_shape(
            type="line",
            x0=df.index[level[0]],
            y0=level[1],
            x1=df.index[-1],
            y1=level[1],
            line=dict(color="Blue" if 'Support' in level[2] else "Red", width=2, dash='dot'),
            xref="x",
            yref="y"
        )
        fig.add_annotation(
            x=df.index[level[0]],
            y=level[1],
            text=level[2],
            showarrow=False,
            yshift=10,
            font=dict(color="Blue" if 'Support' in level[2] else "Red")
        )
    return fig
