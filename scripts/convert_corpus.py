import operator
import sys
from collections import defaultdict, OrderedDict


#sort corpus then: sort -k3,3 -k4,4rn train_edges | less
def make_default_structure(graph_data, word_id):
    if word_id not in graph_data:
        graph_data[word_id] = {
            "word": "",
            "deps": {},
        }


def train_edges(fn_train):
    graph_data = {}
    pos_to_count = defaultdict(lambda: 1)

    with open(fn_train, "r") as f:
        for i, line in enumerate(f):
            if line.startswith("#"):
                continue
            if line == "\n":
                for w in graph_data:
                    for dep in graph_data[w]["deps"]:
                        if "ud_pos" in graph_data[w]:
                            line_key = ""
                            line_key += graph_data[w]["ud_pos"] + ">"

                            if int(dep) < int(w):
                                edge = graph_data[w]["deps"][dep]
                                pos = graph_data[dep]["ud_pos"]
                                line_key += pos + ">" + edge
                                pos_to_count[line_key] += 1
                            elif int(dep) > int(w):
                                edge = graph_data[w]["deps"][dep]
                                pos = graph_data[dep]["ud_pos"]
                                line_key += pos + ">" + edge
                                pos_to_count[line_key] += 1

                graph_data = {}
                continue
            if line != "\n":
                fields = line.split("\t")
                word_id = fields[0]
                word = fields[1]
                ud_pos = fields[3]
                head = fields[6]
                ud_edge = fields[7]

                make_default_structure(graph_data, word_id)
                graph_data[word_id]["word"] = word
                graph_data[word_id]["ud_pos"] = ud_pos

                make_default_structure(graph_data, head)
                graph_data[head]["deps"][word_id] = ud_edge

    sorted_x = sorted(pos_to_count.items(), key=operator.itemgetter(1), reverse=True)
    sorted_dict = OrderedDict(sorted_x)

    dep_to_map = defaultdict(list)
    with open("dep_to_4lang.txt") as map_deps:
        for line in map_deps:
            line = line.strip().split("\t")
            edge_to_map = line[0]
            for map in line[1:]:
                dep_to_map[edge_to_map].append(map)

    with open("train_edges", "w") as out_f:
        for pos in sorted_dict:
            w_from_pos = pos.split(">")[0]
            w_to_pos = pos.split(">")[1]
            w_to_edge = pos.split(">")[2]
            mapping = "\t".join(dep_to_map[w_to_edge])
            out_f.write(
                w_from_pos + "\t" + w_to_pos + "\t" + w_to_edge + "\t" + str(pos_to_count[pos]) + "\t" + mapping + "\n")


def main():
    train_edges(sys.argv[1])


if __name__ == "__main__":
    main()
