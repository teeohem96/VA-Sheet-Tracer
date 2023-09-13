from scipy.spatial import KDTree, cKDTree
import numpy as np
import time
import csv
import matplotlib.pyplot as plt
# borrowed from: https://stackoverflow.com/questions/10818546/finding-index-of-nearest-point-in-numpy-arrays-of-x-and-y-coordinates


def generate_sinewaves():
    pass

def check_bijective_nearest_neighbors():
    pass


def show_stitching_results(flowline_1, flowline_2, distances_2, indices_2, distances_1, indices_1, natural_bijective_indices=[], pseudobijective_indices=[],weighted_midpoints=[],origin = (0,0)):
    fig, ax = plt.subplots()
    flowline_1_x = flowline_1[:,0]
    flowline_1_y = flowline_1[:,1]
    flowline_2_x = flowline_2[:,0]
    flowline_2_y = flowline_2[:,1]
    
    ax.scatter(flowline_1_x, flowline_1_y, c=range(len(flowline_1_x)),cmap="Blues",label="Flowline_1")
    ax.scatter(flowline_2_x, flowline_2_y, c=range(len(flowline_2_x)),cmap="Reds",label="Flowline_2")
    #ax.scatter([flowline_1_x[index] for index in indices_1],[flowline_1_y[index] for index in indices_1], c="yellow",label ="Flowline_1 Source Point")
    #ax.scatter([flowline_2_x[index] for index in indices_2],[flowline_2_y[index] for index in indices_2], c="gold",label = "Flowline_2 Source Point")

    ax.text(flowline_1_x[0], flowline_1_y[0],"Flowline_1 Start Point")
    ax.text(flowline_2_x[0], flowline_2_y[1],"Flowline_2 Start Point")
    ax.plot([origin[0], flowline_1_x[0]],[origin[1], flowline_1_y[0]],  '-',color="purple", alpha=0.95) 
    ax.plot([origin[0], flowline_2_x[0]],[origin[1], flowline_2_y[0]],  '-',color="mediumpurple", alpha=0.95)

    ax.legend(bbox_to_anchor=(0.5, 0), loc='lower center', bbox_transform=fig.transFigure, ncol=4,)
    ax.set_aspect('equal')

##    for i in range(len(indices_2)):
##        flowline_1_point = flowline_1[i]     #indices_2[i]]
##        flowline_2_point = flowline_2[indices_1[i]]
##        distance = [distances_2[i]][0]
##        line_x = [flowline_1_point[0], flowline_2_point[0]]
##        line_y = [flowline_1_point[1], flowline_2_point[1]]
##        ax.plot(line_x, line_y, '-', color="blue", alpha=0.15) #, label="Flowline_1 NN in Flowline 2") #,linewidth=2)
##        #ax.text(flowline_1_point[0], flowline_1_point[1],str(round(distance,2)))
##    
##    for i in range(len(indices_1)):
##        flowline_1_point = flowline_1[indices_2[i]] #indices_2[i]]
##        flowline_2_point = flowline_2[i]
##        distance = [distances_2[i]][0]
##        line_x = [flowline_1_point[0], flowline_2_point[0]]
##        line_y = [flowline_1_point[1], flowline_2_point[1]]
##        ax.plot(line_x, line_y, '-', color="red", alpha=0.15) #, label="Flowline_2 NN in Flowline 1") #,linewidth=2)
##        #ax.text(flowline_1_point[0], flowline_1_point[1],str(round(distance,2)))

    for i in pseudobijective_indices:
        flowline_1_point = flowline_1[indices_2[i]] 
        flowline_2_point = flowline_2[i]
        distance = [distances_2[i]][0]
        line_x = [flowline_1_point[0], flowline_2_point[0]]
        line_y = [flowline_1_point[1], flowline_2_point[1]]
        ax.plot(line_x, line_y, '-', color="yellow", alpha=0.95) #, label="Pseudobijective Connection Line")
        #ax.text(flowline_1_point[0], flowline_1_point[1],str(round(distance,2)))

    for i in natural_bijective_indices:
        flowline_1_point = flowline_1[indices_2[i]] 
        flowline_2_point = flowline_2[i]
        distance = [distances_2[i]][0]
        line_x = [flowline_1_point[0], flowline_2_point[0]]
        line_y = [flowline_1_point[1], flowline_2_point[1]]
        ax.plot(line_x, line_y, '-', color="gold", alpha=0.95) #, label="Natural Bijective Connection Line")
        #ax.text(flowline_1_point[0], flowline_1_point[1],str(round(distance,2)))


    if len(weighted_midpoints) > 0:
        weighted_midpoints_x, weighted_midpoints_y = zip(*weighted_midpoints)
        ax.plot(weighted_midpoints_x, weighted_midpoints_y, '-', color="springgreen", alpha=0.5, label="Weighted Flowline")


    ax.legend(bbox_to_anchor=(0.5, 0), loc='lower center', bbox_transform=fig.transFigure, ncol=3,)

    #plt.show()
    return ax
    

def show_bijective_results(point_field, point_queries, distances, query_indices, pointfield_indices):
    fig, ax = plt.subplots()
    point_field_x   = point_field[:,0]
    point_field_y   = point_field[:,1]
    point_queries_x = point_queries[:,0]
    point_queries_y = point_queries[:,1]
    
    ax.scatter(point_field_x, point_field_y, c="blue",label="Point Field")
    ax.scatter(point_queries_x, point_queries_y, c="red",label="Query Points")
    ax.scatter([point_field_x[index] for index in query_indices],[point_field_y[index] for index in query_indices], c="yellow",label="Pointfield Nearest Point")
    ax.scatter([point_queries_x[index] for index in pointfield_indices],[point_queries_y[index] for index in pointfield_indices], c="gold",label="Query Source Point")

    ax.legend(bbox_to_anchor=(0.5, 0), loc='lower center', bbox_transform=fig.transFigure, ncol=4,)

    ax.set_aspect('equal')

    for i in range(len(query_indices)):
        query_point = point_field[query_indices[i]]
        nearest_point = point_queries[pointfield_indices[i]]
        distance = [distances[i]][0]

        #print("query_point: "+str(query_point)+"\tnearest_point: "+str(nearest_point)+"\tdistance: "+str(distance))

        line_x = [query_point[0], nearest_point[0]]
        line_y = [query_point[1], nearest_point[1]]
        ax.plot(line_x, line_y, '-k')
        ax.text(nearest_point[0], nearest_point[1],str(round(distance,2)))
    
    #plt.show()
    return ax

def get_nearest_neighbor_indices(point_field,point_queries):
    # some research indicates that there are two variants; cKDTree and KDTree; per current docs KDTree is supposed to be preferable, but other sources suggest cKDTree may be marginally faster.  
    search_tree = KDTree(point_field)
    #search_tree = cKDTree(point_field)
    distances, indices = search_tree.query(point_queries)
    return distances, indices

def get_flowlines(path_to_flowlines, flowline_1_filename, flowline_2_filename):

    flowline_1 = []
    flowline_2 = []
    
    with open(path_to_flowlines+flowline_1_filename) as f:
        reader = csv.reader(f)
        flowline_1 = np.asarray(list(np.asarray(line, dtype=np.float32) for line in reader))

    with open(path_to_flowlines+flowline_2_filename) as f:
        reader = csv.reader(f)
        flowline_2 = np.asarray(list(np.asarray(line, dtype=np.float32) for line in reader))

    return flowline_1, flowline_2 

def get_random_pointsets(source_size, query_size, scaling):
    #  generate some queries whose nearest neighbors are to be sought
    point_queries_x = np.random.random(query_size)*scaling
    point_queries_y = np.random.random(query_size)*scaling  
    point_queries = np.dstack([point_queries_x,point_queries_y])[0]

    # generate some source pointfield to query
    point_field_x = np.random.random(source_size)*scaling
    point_field_y = np.random.random(source_size)*scaling  
    point_field = np.dstack([point_field_x,point_field_y])[0]

    return point_queries, point_field



def generate_unified_flowline(flowline_1, flowline_2, subsample_rate=5, search_offset=0, bijection_infill_threshold=3, bijection_infill_style="dense", origin =(3758,3531)):
    print("generating unified flowline...")
    #flowline_2 = np.asarray(list(reversed(list(flowline_2))))
    # print("subsample_rate: "+str(subsample_rate))

    print('flowline lengths:')
    print(len(flowline_1))
    print(len(flowline_2))
    flowline_1 = flowline_1[::subsample_rate]
    flowline_2 = flowline_2[::subsample_rate]

    

    pt_a = np.array((flowline_2[0,0], flowline_2[0,1]))
    pt_b = np.array((flowline_1[0,0], flowline_1[0,1]))

    a1 = np.linalg.norm(pt_a - np.array(origin))
    b1s = np.linalg.norm(flowline_1 - np.array(origin), axis=1)
    # print('b1s: ')
    # print(b1s)
    c1 = np.linalg.norm(flowline_1 - pt_a, axis=1)

    a2 = np.linalg.norm(pt_b - np.array(origin))
    b2s = b1s
    # print('b2s: ')
    # print(b2s)
    c2 = np.linalg.norm(flowline_1 - pt_b, axis=1)

    c_query = np.linalg.norm(pt_a - pt_b)

    angles_a = np.arccos((np.square(a1) + np.square(b1s) - np.square(c1))/(2*a1*b1s))
    angles_b = np.arccos((np.square(a2) + np.square(b2s) - np.square(c2))/(2*a2*b2s))
    query_angle = np.arccos((a1**2 + a2**2 - c_query**2)/(2*a1*a2))

    invalid = np.logical_or(angles_a > query_angle, angles_b > query_angle)
    # print('invalids: ')
    # print(invalid)
    invalid_idx = np.nonzero(invalid)[0]

    if invalid_idx.size:
        flowline_1 = flowline_1[:invalid_idx[0]]

    b1s = np.linalg.norm(flowline_2 - np.array(origin), axis=1)
    c1 = np.linalg.norm(flowline_2 - pt_a, axis=1)

    b2s = b1s
    c2 = np.linalg.norm(flowline_2 - pt_b, axis=1)

    angles_a = np.arccos((np.square(a1) + np.square(b1s) - np.square(c1))/(2*a1*b1s))
    angles_b = np.arccos((np.square(a2) + np.square(b2s) - np.square(c2))/(2*a2*b2s))
    query_angle = np.arccos((a1**2 + a2**2 - c_query**2)/(2*a1*a2))

    invalid = np.logical_or(angles_a > query_angle, angles_b > query_angle)

    # print('query angle:')
    # print(query_angle)
    # print('invalids: ')
    # print(invalid)
    invalid_idx = np.nonzero(invalid)[0]

    if invalid_idx.size:
        flowline_2 = flowline_2[:invalid_idx[0]]

    # print('flowline lengths post-truncation:')
    # print(len(flowline_1))
    # print(len(flowline_2))

    distances_1, indices_1 = get_nearest_neighbor_indices(flowline_2,flowline_1)    # arguments are ordered: search space, then query points
    distances_2, indices_2 = get_nearest_neighbor_indices(flowline_1,flowline_2)

##    print("len(distances_1): "+str(len(distances_1)))
##    print("len(indices_1): "+str(len(indices_1)))
##    print("len(distances_2): "+str(len(distances_2)))
##    print("len(indices_2): "+str(len(indices_2)))

    # find a list of points in flowline_1 whose nearest neighbors nearest neighbor is that point
    #  e.g. if point at index 2 in flowline_1 has a nearest neighbor at index 5 in flow_line_2 AND, the point at index 5 in flowline_2 has a nearest neighbor at index 2 in flowline_1, then add index 2 to the list of flowline_1 bijective indices
    natural_bijective_indices_1 = []
    natural_bijective_indices_2 = []
    natural_bijective_distances = []
    
    for i in range(len(indices_1)):
        if indices_2[indices_1[i]] == i:
            natural_bijective_indices_1.append(indices_1[i])
            natural_bijective_indices_2.append(i)
            natural_bijective_distances.append(distances_1[i])

    # print("len(natural_bijective_indices_1): "+str(len(natural_bijective_indices_1)))
    # print(natural_bijective_distances)
    # print('nbi1:')
    # print(natural_bijective_indices_1)

    # list of induced bijections 
    pseudobijective_indices_1 = []
    pseudobijective_indices_2 = []
    
    # for each bijection:
    for i in range(len(natural_bijective_indices_1)-1):
        natural_bijective_index_1_start = natural_bijective_indices_1[i]
        natural_bijective_index_1_end = natural_bijective_indices_1[i+1]
        natural_bijective_index_2_start = natural_bijective_indices_2[i]
        natural_bijective_index_2_end = natural_bijective_indices_2[i+1]
        #print("natural_bijective_index_1_start: "+str(natural_bijective_index_1_start)+"\tnatural_bijective_index_1_end: "+str(natural_bijective_index_1_end)+
             # "\tnatural_bijective_index_2_start: "+str(natural_bijective_index_2_start)+"\tnatural_bijective_index_2_end: "+str(natural_bijective_index_2_end))

        # print('nbi1start, end:')
        # print(natural_bijective_index_1_start)
        # print(natural_bijective_index_1_end)
        
        natural_segment_len_1 = abs(natural_bijective_index_1_end - natural_bijective_index_1_start)
        natural_segment_len_2 = abs(natural_bijective_index_2_end - natural_bijective_index_2_start) 
        # if the bijective lines are far enough apart, generate more bijection lines between them (don't need to do this if they're right next to each other)
        if max(natural_segment_len_1, natural_segment_len_2) > bijection_infill_threshold:

            # select a master flowline segment from the two segments that fall between this bijection and the next (select the segment with fewer points for speed, and with more points for line precision)
            # note: replace "slave" language when code is working

            if (bijection_infill_style == "dense") != (natural_segment_len_2 > natural_segment_len_1):
                master_indices = (natural_bijective_index_1_start, natural_bijective_index_1_end)
                slave_indices = (natural_bijective_index_2_start, natural_bijective_index_2_end)
                master_infill = pseudobijective_indices_1
                slave_infill = pseudobijective_indices_2
                # abusing mutability of lists is bad for readability, change my mind
            elif bijection_infill_style == "sparse" or bijection_infill_style == "dense": # this is awful for readability but is a consequence of using xor
                master_indices = (natural_bijective_index_2_start, natural_bijective_index_2_end)
                slave_indices = (natural_bijective_index_1_start, natural_bijective_index_1_end)
                master_infill = pseudobijective_indices_2
                slave_infill = pseudobijective_indices_1
            else:
                print("WARNING: \""+str(bijection_infill_style)+"\" is an invalid infill style; must be one of \"dense\" or \"sparse\"")
            
            distance = abs(master_indices[1] - master_indices[0])
            master_infill.extend(np.linspace(master_indices[0], master_indices[1], distance, endpoint=False))
            slave_infill.extend(np.linspace(slave_indices[0], slave_indices[1], distance, endpoint=False))

        else:
            pseudobijective_indices_1.append(natural_bijective_index_1_start)
            pseudobijective_indices_2.append(natural_bijective_index_2_start)

    if len(natural_bijective_indices_1) <= 1:
        pseudobijective_indices_1.append(natural_bijective_indices_1[0])
        pseudobijective_indices_2.append(natural_bijective_indices_2[0])
    else:
        pseudobijective_indices_1.append(natural_bijective_indices_1[-1])
        pseudobijective_indices_2.append(natural_bijective_indices_2[-1])

    # PART WHERE THE INTERPOLATION SECTION ENDS
    bijective_indices_1 = [int(round(n, 0)) for n in pseudobijective_indices_1]
    bijective_indices_2 = [int(round(n, 0)) for n in pseudobijective_indices_2]
            
##    print("len(bijective_indices_1): "+str(len(bijective_indices_1)))
##    print("len(bijective_indices_2): "+str(len(bijective_indices_2)))

    # get index of first bijection
    bijection_start_1 = min(bijective_indices_1)
    # get index of last bijection
    bijection_start_2 = min(bijective_indices_2)
    transition_idx = np.argmin(np.array(natural_bijective_distances))
    transition_point_1 = natural_bijective_indices_1[transition_idx]
    transition_point_2 = natural_bijective_indices_2[transition_idx]

    # print("transition 1:")
    # print(transition_point_1)

    # print("transition 2:")
    # print(transition_point_2)

    # print("bijection_start_1: "+str(bijection_start_1))
    # print("bijective_indices_1[0]: "+str(bijective_indices_1[0]))
    # print("bijective_indices_1[-1]: "+str(bijective_indices_1[-1]))
    # print("bijection_start_2: "+str(bijection_start_2))
    
    # calculate the weighted midpoints for flowlines for the segment between the first and last bijections (could be all of both lines, or only a midsection with a "tail" at one or either end)
    weighted_midpoints = []
    for i in range(len(bijective_indices_1)):
        bijective_index_pair = [bijective_indices_2[i],bijective_indices_1[i]]
        bijective_spatial_points = [flowline_1[bijective_index_pair[0]], flowline_2[bijective_index_pair[1]]]

        # calculate fractional representation of bijective segment (should range from 1.0 to 0.0)
        

        try:
        # Floor Division : Gives only Fractional Part as Answer
            if transition_point_2-bijection_start_2 != 0:
                flowline_1_pc = max(1 - ((bijective_index_pair[0] - bijection_start_2)/(transition_point_2-bijection_start_2))**2, 0)
            else:
                flowline_1_pc = 0

            # print('pc1:')
            # print(flowline_1_pc)
            # print('idx:')
            # print(bijective_index_pair[0])

            if transition_point_1-bijection_start_1 != 0:
                flowline_2_pc = max(1 - ((bijective_index_pair[1] - bijection_start_1)/(transition_point_1-bijection_start_1))**2, 0)
            else:
                flowline_2_pc = 0
            # print('pc2:')
            # print(flowline_2_pc)
            # print('idx:')
            # print(bijective_index_pair[1])

            norm_pc = 1 - flowline_1_pc - flowline_2_pc
            # print('norm pc:')
            # print(norm_pc)
        except ZeroDivisionError: #deprecated, this really shouldn't happen anymore
            print("WARNING: Gap detected in sheet. Interpolation will be linear across gap")
            flowline_1_pc = 0.5

        
        #print("bijective_index_pair: "+str(bijective_index_pair)+"\tbijective_spatial_points: "+str(bijective_spatial_points[0])+", "+str(bijective_spatial_points[1])+"\tflowline_2["+str(bijective_index_pair[1])+"]: "+str(flowline_2[bijective_index_pair[1]])+"\tflowline_1_pc: "+str(round(flowline_1_pc,2)))
        weighted_midpoint_x = flowline_1_pc*flowline_1[bijective_index_pair[0]][0] + (flowline_2_pc)*flowline_2[bijective_index_pair[1]][0] + norm_pc*(flowline_1[bijective_index_pair[0]][0] + flowline_2[bijective_index_pair[1]][0])/2
        weighted_midpoint_y = flowline_1_pc*flowline_1[bijective_index_pair[0]][1] + (flowline_2_pc)*flowline_2[bijective_index_pair[1]][1] + norm_pc*(flowline_1[bijective_index_pair[0]][1] + flowline_2[bijective_index_pair[1]][1])/2
        weighted_midpoint = [round(weighted_midpoint_x,4), round(weighted_midpoint_y,4)]
        weighted_midpoints.append(weighted_midpoint)
        #print("flowline_1_pc: "+str(round(flowline_1_pc,2))+"\tflowline_1["+str(bijective_index_pair[0])+"]: "+str(flowline_1[bijective_index_pair[0]])+"\tweighted_midpoint: "+str(weighted_midpoint)+"\tflowline_2["+str(bijective_index_pair[1])+"]: "+str(flowline_2[bijective_index_pair[1]]))

    # check for any "tail" segments that are not covered by the range of available bijections
    tail_1 = flowline_1[0:bijection_start_2] #[::-1]  # NOTE:  not 100% sure if this needs to be reversed for this one (second one def needs it); if green line shenanigans try omitting
    tail_2 = flowline_2[0:bijection_start_1][::-1]
    #print("tail_1: "+str(tail_1))
    #print("tail_2: "+str(tail_2))
    # graft on any existing "tail" points that are exclusively (i.e. 100% weighted towards) flowline_1 or flowline_2
    weighted_midpoints = np.concatenate([tail_1, weighted_midpoints,tail_2])


    # option to save/display visual of flowline
    # DON'T ENABLE THIS WHEN RUNNING THE GUI
    '''
    ax1 = show_stitching_results(flowline_1, flowline_2, distances_2, indices_2, distances_1, indices_1, natural_bijective_indices=natural_bijective_indices_1, pseudobijective_indices=bijective_indices_1,weighted_midpoints=weighted_midpoints)
    plt.show()
    print("done.")
    '''
    return weighted_midpoints
    
##def main():
##
##    path_to_flowlines = "test_flowlines\\"
##    flowline_1_filename = "sampleline1.csv"
##    flowline_2_filename = "sampleline2.csv"
##
##    flowline_1, flowline_2 = get_flowlines(path_to_flowlines, flowline_1_filename, flowline_2_filename)
##
##    flowline_1_size = len(flowline_1)
##    flowline_2_size = len(flowline_2)
##    print("flowline_1_size: "+str(flowline_1_size))
##    print("flowline_2_size: "+str(flowline_2_size))
##
##    # MAGIC NUMBERS
##    subsample_rate              = 10           # sample every nth point of both flowlines
##    search_offset               = 0             # step offset for nearest neighbors in the search process
##    bijection_infill_threshold  = 3             # if the indexes of two natural bijection lines are closer than nearer than this value, don't both to infill with induced bijection lines 
##    bijection_infill_style      = "dense"       # one of either "dense" or "sparse" ("sparse" speeds up runtime at the cost of less detail, "dense" gives move detail at the cost of longer runtime.  basically this flag determines whether to mappoints against the longer or short inter-bijection flowline segment
##    print("window size: "+str(list(range(-search_offset,search_offset+1))))
##    
##
##        
##         
##    #print("weighted_midpoints: "+str(weighted_midpoints))
##    #ax1 = show_bijective_results(flowline_2, flowline_1, bijective_distances_1, bijective_indices_1,bijective_indices_2)
##    # plt.show()
##
##
##
##
##if __name__ == "__main__":
##    main()
##
