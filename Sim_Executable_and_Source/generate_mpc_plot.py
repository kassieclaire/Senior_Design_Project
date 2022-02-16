
import matplotlib.pyplot
from pandapower.plotting import cmap_continuous, create_bus_trace, draw_traces
from pandapower.plotting import cmap_discrete, create_line_trace, draw_traces
import pandapower.plotting
import pandapower.converter
import pandapower.networks
import pandapower


# MPC_PATH = '.\\Sim_Executable_and_Source\\test_struct.mat'
# mpc = pandapower.converter.from_mpc(MPC_PATH)
# MPC_PATH = '.\\Sim_Executable_and_Source\\test_mpc_2.mat'
# note: the variable name saved from matlab becomes the casename_mpc_file
# do matlab save with save(filename, var (as string)) where the variable is just the raw mpc
# mpc = pandapower.converter.from_mpc(MPC_PATH, casename_mpc_file='m2')

MPC_PATH = '.\\Sim_Executable_and_Source\\mpc_case118_2.mat'
mpc = pandapower.converter.from_mpc(MPC_PATH)
# mpc = pandapower.networks.case118()

print(mpc)
print(type(mpc))

# simple plotting
# pandapower.plotting.simple_plot(mpc)


# discrete colormap
cmap_list = [((-10, 0), "green"), ((0, 70), "blue"), ((70, 150), "yellow")]
cmap, norm = cmap_discrete(cmap_list)
# lc = create_line_trace(mpc, cmap=cmap, cmap_vals=[
#                        ((-1)**x + 1) for x in range(37)])
# lc = create_line_trace(mpc, cmap=cmap)
# draw_traces(lc, map_style='streets')
# pandapower.plotting.draw_collections([lc])

# continuous colormap
cmap_list = [(0.97, "blue"), (1.0, "green"), (1.03, "red")]
cmap, norm = cmap_continuous(cmap_list)
# bc = create_bus_trace(mpc, cmap=cmap, cmap_vals=[
# ((-1)**x + 1) for x in range(37)], cmin = 0, cmax = 2)
# draw_traces(bc)

# collection based plotting
if len(mpc.line_geodata) == 0 and len(mpc.bus_geodata) == 0:
    pandapower.plotting.create_generic_coordinates(mpc)
pandapower.plotting.create_gen_collection
cmap_list = [(0.97, "blue"), (1.0, "green"), (1.03, "red")]
cmap, norm = cmap_continuous(cmap_list)
# line_collection = pandapower.plotting.create_line_collection(
#     mpc, cmap=cmap, norm=norm)
bus_collection = pandapower.plotting.create_bus_collection(
    mpc, size=0.05)
line_collection = pandapower.plotting.create_line_collection(
    mpc, use_bus_geodata=True)
trafo_collection = pandapower.plotting.create_trafo_collection(mpc)
# pc = pandapower.plotting.draw_collections(
#     [bus_collection, line_collection, trafo_collection])
# print(pc)
# print(type(pc))
# matplotlib.pyplot.show()
# pc.figure

# Section modified from pandapower simple_plot.py simple_plot()
# create geodata if not in mpc
if len(mpc.line_geodata) == 0 and len(mpc.bus_geodata) == 0:
    print("No or insufficient geodata available --> Creating artificial coordinates." +
          " This may take some time")
    pandapower.plotting.create_generic_coordinates(
        mpc, respect_switches=True)

bus_size = 1.0
ext_grid_size = 1.0
trafo_size = 1.0
sgen_size = 1.0
load_size = 1.0
switch_size = 2.0
switch_distance = 1.0
gen_size = 1.0

# if scale_size -> calc size from distance between min and max geocoord
sizes = pandapower.plotting.get_collection_sizes(mpc, bus_size, ext_grid_size, trafo_size,
                                                 load_size, sgen_size, switch_size, switch_distance, gen_size)
bus_size = sizes["bus"]
ext_grid_size = sizes["ext_grid"]
trafo_size = sizes["trafo"]
sgen_size = sizes["sgen"]
load_size = sizes["load"]
switch_size = sizes["switch"]
switch_distance = sizes["switch_distance"]
gen_size = sizes["gen"]
# create bus collections to plot
cmap_list = [((0.0, 200), "blue"), ((200, 500), "yellow")]
cmap, norm = cmap_discrete(cmap_list)
# bc = pandapower.plotting.create_bus_collection(
#     mpc, mpc.bus.index, size=bus_size, color="b", zorder=10)
bc = pandapower.plotting.create_bus_collection(
    mpc, mpc.bus.index, size=bus_size, color="b", cmap=cmap, norm=norm, z=mpc.bus['vn_kv'])
# if bus geodata is available, but no line geodata
use_bus_geodata = len(mpc.line_geodata) == 0
in_service_lines = mpc.line[mpc.line.in_service].index
nogolines = set(mpc.switch.element[(mpc.switch.et == "l") & (mpc.switch.closed == 0)]) \
    if True else set()
plot_lines = in_service_lines.difference(nogolines)

cmap_list = [((0.0, 0.01), "red"), ((0.01, 1), "black")]
cmap, norm = cmap_discrete(cmap_list)

# create line collections
# lc = pandapower.plotting.create_line_collection(mpc, plot_lines, color="grey", cmap=cmap, norm=norm, linewidths=1.0,
#                                                 use_bus_geodata=use_bus_geodata)
lc = pandapower.plotting.create_line_collection(mpc, plot_lines, cmap=cmap, norm=norm, linewidths=2.0,
                                                use_bus_geodata=use_bus_geodata, z=[1 if x != float('inf') else 0 for x in mpc.line['r_ohm_per_km']])
collections = [bc, lc]
# create ext_grid collections
# eg_buses_with_geo_coordinates = set(net.ext_grid.bus.values) & set(net.bus_geodata.index)
if len(mpc.ext_grid) > 0:
    sc = pandapower.plotting.create_ext_grid_collection(mpc, size=ext_grid_size, orientation=0,
                                                        ext_grids=mpc.ext_grid.index, patch_edgecolor="y",
                                                        zorder=11)
    collections.append(sc)
# create trafo collection if trafo is available
trafo_buses_with_geo_coordinates = [t for t, trafo in mpc.trafo.iterrows()
                                    if trafo.hv_bus in mpc.bus_geodata.index and
                                    trafo.lv_bus in mpc.bus_geodata.index]
if len(trafo_buses_with_geo_coordinates) > 0:
    tc = pandapower.plotting.create_trafo_collection(mpc, trafo_buses_with_geo_coordinates,
                                                     color="k", size=trafo_size)
    collections.append(tc)
# create trafo3w collection if trafo3w is available
trafo3w_buses_with_geo_coordinates = [
    t for t, trafo3w in mpc.trafo3w.iterrows() if trafo3w.hv_bus in mpc.bus_geodata.index and
    trafo3w.mv_bus in mpc.bus_geodata.index and trafo3w.lv_bus in mpc.bus_geodata.index]
if len(trafo3w_buses_with_geo_coordinates) > 0:
    tc = pandapower.plotting.create_trafo3w_collection(mpc, trafo3w_buses_with_geo_coordinates,
                                                       color="k")
    collections.append(tc)
if True and len(mpc.switch):
    sc = pandapower.plotting.create_line_switch_collection(
        mpc, size=switch_size, distance_to_bus=switch_distance,
        use_line_geodata=not use_bus_geodata, zorder=12, color="k")
    collections.append(sc)


if False and len(mpc.load):
    lc = pandapower.plotting.create_load_collection(mpc, size=load_size)
    collections.append(lc)
if len(mpc.switch):
    bsc = pandapower.plotting.create_bus_bus_switch_collection(
        mpc, size=switch_size)
    collections.append(bsc)
ax = pandapower.plotting.draw_collections(
    collections, ax=None, plot_colorbars=False)

matplotlib.pyplot.show()
