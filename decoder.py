from core import *
from distributions import *

def get_degrees_from(distribution_name, N, k):
    """ Returns the random degrees from a given distribution of probabilities.
    The degrees distribution must look like a Poisson distribution and the
    degree of the first drop is 1 to ensure the start of decoding.
    """

    if distribution_name == "ideal":
        probabilities = ideal_distribution(N)
    elif distribution_name == "robust":
        probabilities = robust_distribution(N)
    else:
        probabilities = None

    population = list(range(0, N+1))
    return np.random.choice(population, k, p=probabilities) #[1] + choices(population, probabilities, k=k-1)

def encode(l, k,start_index):
    """ Iterative encoding - Encodes new symbols and yield them.
    Encoding one symbol is described as follow:
    1.  Randomly choose a degree according to the degree distribution, save it into "deg"
        Note: below we prefer to randomly choose all the degrees at once for our symbols.
    2.  Choose uniformly at random 'deg' distinct input blocs.
        These blocs are also called "neighbors" in graph theory.
    3.  Compute the output symbol as the combination of the neighbors.
        In other means, we XOR the chosen blocs to produce the symbol.
    """

    # Display statistics
    # print("Generating grap    h...")
    blocks_n = l
    #assert blocks_n <= drops_quantity, "Because of the unicity in the random neighbors, it is need to drop at least the same amount of blocks"

    start_time = time.time()

    # Generate random indexes associated to random degrees, seeded with the symbol id
    random_degrees = get_degrees_from("robust", blocks_n, k)

    # print("Ready for encoding.", flush=True)

    for i in range(k):

        # Get the random selection, generated precedently (for performance)
        selection_indexes, deg = generate_indexes(random_degrees[i], blocks_n)

        # Xor each selected array within each other gives the drop (or just take one block if there is only one selected)
        # drop = blocks[selection_indexes[0]]
        # for n in range(1, deg):
            # drop = np.bitwise_xor(drop, blocks[selection_indexes[n]])
            # drop = drop ^ blocks[selection_indexes[n]] # according to my tests, this has the same performance

        # Create symbol, then log the process
        symbol = Symbol(index=start_index+i, degree=deg, neighbors = selection_indexes)

        # if VERBOSE:
        #     symbol.log(blocks_n)
        # # print("VERBOSE")
        # log("Encoding", i, k, start_time)

        yield symbol

    # print("\n----- Correctly dropped {} symbols (packet size={})".format(k, PACKET_SIZE))


# def recover_graph(symbols, blocks_quantity):
#     """ Get back the same random indexes (or neighbors), thanks to the symbol id as seed.
#     For an easy implementation purpose, we register the indexes as property of the Symbols objects.
#     """
#
#     for symbol in symbols:
#
#         neighbors, deg = generate_indexes(symbol.index, symbol.degree, blocks_quantity)
#         symbol.neighbors = {x for x in neighbors}
#         symbol.degree = deg
#         if VERBOSE:
#             symbol.log(blocks_quantity)
#
#     return symbols

def reduce_neighbors(block_index, symbols):
    """ Loop over the remaining symbols to find for a common link between
    each symbol and the last solved block `block`

    To avoid increasing complexity and another for loop, the neighbors are stored as dictionnary
    which enable to directly delete the entry after XORing back.
    """

    for other_symbol in symbols:
        if other_symbol.degree > 1 and block_index in other_symbol.neighbors:

            # XOR the data and remove the index from the neighbors
            # other_symbol.data = np.bitwise_xor(blocks[block_index], other_symbol.data)
            other_symbol.neighbors.remove(block_index)

            other_symbol.degree -= 1

            # if VERBOSE:
            #     print("XOR block_{} with symbol_{} :".format(block_index, other_symbol.index), list(other_symbol.neighbors))


def SEF_decode(blockindices):
    """ Iterative decoding - Decodes all the passed symbols to build back the data as blocks.
    The function returns the data at the end of the process.

    1. Search for an output symbol of degree one
        (a) If such an output symbol y exists move to step 2.
        (b) If no output symbols of degree one exist, iterative decoding exits and decoding fails.

    2. Output symbol y has degree one. Thus, denoting its only neighbour as v, the
        value of v is recovered by setting v = y.

    3. Update.

    4. If all k input symbols have been recovered, decoding is successful and iterative
        decoding ends. Otherwise, go to step 1.
    """
    # symbols = []
    file_symbols = []
    a = 0
    bootstrap = 0
    l = 1000
    k = 1
    decodelen = len(blockindices)
    decodeflag = np.zeros(decodelen)
    while np.sum(decodeflag) < decodelen:
        for curr_symbol in encode(l,k,a):
            a = a + 1
            file_symbols.append(curr_symbol)
            # print("symbols",a,len(file_symbols))
        symbols = file_symbols.copy()
        # print(symbols1.index)
        symbols_n = len(symbols)
        # print('a',symbols_n, curr_symbol.degree ,'done ',np.sum(decodeflag),'/',decodelen)
        #symbols = recover_graph(symbols, l)

        solved_blocks_count = 0
        iteration_solved_count = 1
        bootstrap = bootstrap + 1
        start_time = time.time()

        while iteration_solved_count > 0:# or solved_blocks_count == 0:
            iteration_solved_count = 0
            for i, symbol in enumerate(symbols):
                # Check the current degree. If it's 1 then we can recover data
                if symbol.degree == 1:
                    iteration_solved_count += 1
                    block_index = next(iter(symbol.neighbors))
                    if block_index in blockindices:
                        decodeflag[blockindices.index(block_index)] = 1
                    symbols.pop(i)

                    # This symbol is redundant: another already helped decoding the same block
                    # if blocks[block_index] is not None:
                    #     continue

                    solved_blocks_count += 1
                    # print('hello hello hello hello hello hello hello hello hello hello hello hello hello hello hello hello ',solved_blocks_count,symbol.index)
                    log("Decoding", solved_blocks_count, l, start_time)

                    # Reduce the degrees of other symbols that contains the solved block as neighbor
                    reduce_neighbors(block_index,  symbols)
            # if solved_blocks_count == 0
    #print("\n----- Solved Blocks {:2}/{:2} --".format(solved_blocks_count, blocks_n))
    print('a',symbols_n,'done ',np.sum(decodeflag),'/',decodelen)

    print(bootstrap)
    return bootstrap
