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
    b2s = np.linalg.norm(flowline_1 - np.array(origin), axis=1)
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
    flowline_1 = flowline_1[invalid==0]

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
    

    # natural_bijective_distances_1 = []

    for i in range(search_offset,len(indices_1)-search_offset): #[:100]:
        i_list = range(i-search_offset,i+search_offset+1)
        #print("i: "+str(i))
        index_1         = indices_1[i]
        point_2         = flowline_2[index_1]
        distance_1      = distances_1[i]
        #lin_diff        = abs(flowline_2 - point_2)
        #print("lin_diff: "+str(lin_diff))

        j_list = []
        offset_start = -search_offset
        offset_stop = search_offset+1
        offsets = list(range(offset_start,offset_stop))

        # iteratively check for bijective-ish connections between local point slices based on the offset range
        # note this only goes in one direction (from flowline_1 to flowline_2); the reverse case is easy since we can check to see if the nearest neighbor to flowline_2 in flowline_1 in in i_list
        # it's kind of a cats cradle if you need a visual
        for offset in offsets:
            flowline_2_rolled = np.roll(flowline_2,offset)  # "roll" flowline_2 through the range of offsets to see if any of the instances match up with the hit from flowline_1
            #print("flowline_2_rolled: "+str(flowline_2_rolled))
            j_candidates = np.where(flowline_2_rolled == point_2)[0]
            #print("j: "+str(j_candidates))
            if len(j_candidates) > 0:
                j_list.append(j_candidates[0])

        # if there are multiple matches, consider the midpoint j value to be the best approximate of bijectivity
        if len(j_list) > 0:
            #print("j_list: "+str(j_list))
            j = j_list[int(len(j_list)/2)]
                
        index_2         = indices_2[j]
        distance_2      = distances_2[j]

        if (index_2 in i_list) and (index_1 in j_list):
            #print("i: "+str(i)+"\tindex_2: "+str(index_2)+"\tj: "+str(j)+"\tindex_1:"+str(index_1)+"\tdistance_1: "+str(distance_1)+"\tdistance_2: "+str(distance_2))
            slice_2_start = i-search_offset
            slice_2_stop  = i+search_offset
            slice_1_start = j-search_offset
            slice_1_stop  = j+search_offset

            #print("slice_2_start: "+str(slice_2_start)+"\tslice_2_stop: "+str(slice_2_stop)+"\tslice_1_start: "+str(slice_1_start)+"\tslice_1_stop: "+str(slice_1_stop))
            slice_2 = indices_2[slice_2_start:slice_2_stop+1]
            slice_1 = indices_1[slice_1_start:slice_1_stop+1]
            #print("slice_2: "+str(slice_2)+"\tslice_1: "+str(slice_1))

            natural_bijective_indices_1.append(index_1)
            natural_bijective_indices_2.append(index_2)
            # natural_bijective_distances_1.append(distances_1[i])    # note: you could do this for flowline 2, but it should be the same number, so omitting for now

    print("len(natural_bijective_indices_1): "+str(len(natural_bijective_indices_1)))
##    print("len(natural_bijective_indices_2): "+str(len(natural_bijective_indices_2)))
    #print("bijective_indices_1: "+str(bijective_indices_1))
    #natural indices done


    

    # ax = show_stitching_results(flowline_1, flowline_2, distances_2, indices_2, distances_1, indices_1, natural_bijective_indices=natural_bijective_indices_1, origin = origin)
    # ax.scatter(origin[0], origin[1])
    # ax.text(origin[0], origin[1],"Origin")
    
    
    # plt.show()


    #natural_angles_1 = [np.arctan2(flowline_2[1])]
    # list of induced bijections 
    pseudobijective_indices_1 = []
    pseudobijective_indices_2 = []
    
    # combined list of natural and induced bijections 
    # bijective_indices_1 = pseudobijective_indices_1 #[]
    # bijective_indices_2 = pseudobijective_indices_2 #[]
    # bijective_distances_1 = []  # note this is not a full list of distances; for now we add -1 for any pseudobijection <--- I don't really use this list so I didn't actually add the -1s 

    #ax1 = show_stitching_results(flowline_1, flowline_2, distances_2, indices_2, distances_1, indices_1) #, natural_bijective_indices=natural_bijective_indices_1) #, pseudobijective_indices=bijective_indices_1,weighted_midpoints=weighted_midpoints)
    #plt.show()
    
    # for each bijection:
    for i in range(len(natural_bijective_indices_1)-1):
        natural_bijective_index_1_start = natural_bijective_indices_1[i]
        natural_bijective_index_1_end = natural_bijective_indices_1[i+1]
        natural_bijective_index_2_start = natural_bijective_indices_2[i]
        natural_bijective_index_2_end = natural_bijective_indices_2[i+1]
        #print("natural_bijective_index_1_start: "+str(natural_bijective_index_1_start)+"\tnatural_bijective_index_1_end: "+str(natural_bijective_index_1_end)+
             # "\tnatural_bijective_index_2_start: "+str(natural_bijective_index_2_start)+"\tnatural_bijective_index_2_end: "+str(natural_bijective_index_2_end))
        
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

    # PART WHERE THE INTERPOLATION SECTION ENDS
    bijective_indices_1 = [int(round(n, 0)) for n in pseudobijective_indices_1]
    bijective_indices_2 = [int(round(n, 0)) for n in pseudobijective_indices_2]
            
##    print("len(bijective_indices_1): "+str(len(bijective_indices_1)))
##    print("len(bijective_indices_2): "+str(len(bijective_indices_2)))

    # get index of first bijection
    bijection_start_1 = min(bijective_indices_1)
    # get index of last bijection
    bijection_start_2 = min(bijective_indices_2)
##    print("bijection_start_1: "+str(bijection_start_1))
##    print("bijective_indices_1[0]: "+str(bijective_indices_1[0]))
##    print("bijective_indices_1[-1]: "+str(bijective_indices_1[1]))
##    print("bijection_start_2: "+str(bijection_start_2))
    
    # calculate the weighted midpoints for flowlines for the segment between the first and last bijections (could be all of both lines, or only a midsection with a "tail" at one or either end)
    weighted_midpoints = []
    for i in range(len(bijective_indices_1)):
        bijective_index_pair = [bijective_indices_2[i],bijective_indices_1[i]]
        bijective_spatial_points = [flowline_1[bijective_index_pair[0]], flowline_2[bijective_index_pair[1]]]

        # calculate fractional representation of bijective segment (should range from 1.0 to 0.0)
        

        try:
        # Floor Division : Gives only Fractional Part as Answer
            flowline_1_pc = 1 - (bijection_start_2-bijective_index_pair[0])/((bijection_start_2-bijective_index_pair[0])+(bijection_start_1-bijective_index_pair[1]))
        except ZeroDivisionError:
            print("div by zero btw")
            flowline_1_pc = 0.5

        
        #print("bijective_index_pair: "+str(bijective_index_pair)+"\tbijective_spatial_points: "+str(bijective_spatial_points[0])+", "+str(bijective_spatial_points[1])+"\tflowline_2["+str(bijective_index_pair[1])+"]: "+str(flowline_2[bijective_index_pair[1]])+"\tflowline_1_pc: "+str(round(flowline_1_pc,2)))
        weighted_midpoint_x = flowline_1_pc*flowline_1[bijective_index_pair[0]][0] + (1 - flowline_1_pc)*flowline_2[bijective_index_pair[1]][0]
        weighted_midpoint_y = flowline_1_pc*flowline_1[bijective_index_pair[0]][1] + (1 - flowline_1_pc)*flowline_2[bijective_index_pair[1]][1]
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
