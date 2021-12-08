from django.shortcuts import render
from django.contrib import messages
from django.http import HttpResponse
import random


def home(request):
    return render(request, 'generator/home.html')


def graph(request):

    gr_type = int(request.GET.get('graph_type'))
    n = int(request.GET.get('vertices'))
    task_type = int(request.GET.get('task_type'))
    min_edges = int(request.GET.get('min_edges'))
    max_edges = int(request.GET.get('max_edges'))
    min_weight = int(request.GET.get('min_weight'))
    max_weight = int(request.GET.get('max_weight'))
    edges_in_ans = int(request.GET.get('edges_in_answer'))
    num_of_ans = int(request.GET.get('num_of_answers'))
    num_of_grs = int(request.GET.get('num_of_graphs'))

    if (min_edges + 2 >= max_edges) | (min_edges < n + num_of_ans) | (min_edges > (n - 1) * n / 2):
        messages.error(request, 'Некорректно задано количество рёбер в графе')
        return render(request, 'generator/home.html', {})
    elif min_weight * 2 >= max_weight:
        messages.error(request, 'Некорректно заданы допустимые веса рёбер')
        return render(request, 'generator/home.html', {})
    elif edges_in_ans >= n - 1:
        messages.error(request, 'Некорректно задано количество дуг в кратчайшем пути')
        return render(request, 'generator/home.html', {})
    else:
        out = check_params(gr_type, n, task_type, min_edges, max_edges, min_weight, max_weight, edges_in_ans, num_of_ans, num_of_grs)

    if out['fail'] == 1:
        messages.error(request, 'Похоже, нам не удалось сгенерировать граф(ы) по заданным параметрам. Измените их и попробуйте снова!')
        return render(request, 'generator/home.html', {})
    return render(request, 'generator/graph.html', out)


def check_params(gr_type, n, task_type, min_edges, max_edges, min_weight, max_weight, edges_in_ans, num_of_ans, num_of_grs):

    inf = max_weight + 1  # для обозначения несуществующих рёбер
    flag_recount = attempts = 0
    outputs = []
    keeper = num_of_ans
    fail = 0

    for f in range(num_of_grs):
        flag_recount, attempts = 0, 0
        while (flag_recount == 0) & (attempts < 10):
            num_of_ans = keeper
            attempts += 1
            m = []  # matrix
            way_to_vertice = []  # кратчайший путь (список врешин) до каждой из вершин

            for x in range(n):
                way_to_vertice.append([])
                m.append([inf] * n)

            way_to_vertice[0] = [0]
            ans = []  # список, содержащий кратчайшие пути
            ways = [0] * n  # список длин кратчайших путей до каждой из вершин
            marks = [[0, 0]]  # список содержит порядок помечания вершин (уровень относительно x0 и номер вершины)

            arr = [i for i in range(1, n - 1)]
            random.shuffle(arr)

            ans.append([0] + arr[:(edges_in_ans - 1)] + [n - 1])

            for i in range(edges_in_ans):     # генерация кратчайшего пути, заполнение путей до вершин и порядка помечания
                cur, son = ans[0][i], ans[0][i + 1]
                m[cur][son] = random.randint(min_weight, max_weight - 2)
                if gr_type == 1:
                    m[son][cur] = m[cur][son]
                ways[son] = ways[cur] + m[cur][son]
                way_to_vertice[son] = way_to_vertice[cur] + [son]
                marks.append([i + 1, son])

            for i in arr[(edges_in_ans - 1):]:   # присоединение вершин, не входящих в кратчайший путь
                parent = random.choice(ans[0][:edges_in_ans])
                m[parent][i] = random.randint(min_weight + 2, max_weight)
                if gr_type == 1:
                    m[i][parent] = m[parent][i]
                ways[i] = ways[parent] + m[parent][i]
                way_to_vertice[i] = way_to_vertice[parent] + [i]
                order = ans[0].index(parent) + 1
                marks.append([order, i])
                marks.sort()

            checking_arr = marks.copy()

            def index_by_second_element(elem):
                for c in range(n):
                    if marks[c][1] == elem:
                        return c
                return 0

            for i in marks:
                for j in range(n):
                    if (i[1] == j) | (m[i[1]][j] != inf):
                        continue
                    if ways[j] < ways[i[1]] + max_weight:
                        new_position = i[0] + 1
                        checking_arr.append([new_position, j])
                        checking_arr.sort()
                        old_index = index_by_second_element(j)
                        if old_index > checking_arr.index([new_position, j]):
                            m[i[1]][j] = random.randint(max(ways[j] - ways[i[1]] + 1, min_weight), max_weight)
                            if gr_type == 1:
                                m[j][i[1]] = m[i[1]][j]
                            flag_recount = 1
                            break
                        checking_arr.remove([new_position, j])

            k = n
            num_of_ans -= 1

            while k < min_edges:   # можно идти в уже отмеченные
                marked = [0] * n
                for i in marks:
                    marked[i[1]] = 1
                    for j in range(n):
                        if (i[1] == j) | (m[i[1]][j] != inf):
                            continue
                        if (num_of_ans > 0) & (ans[0].count(j)) & (marked[j] == 1) & (ways[j] - ways[i[1]] >= min_weight) & (ways[j] - ways[i[1]] <= max_weight):  # добавление ещё одного кр. пути
                            m[i[1]][j] = ways[j] - ways[i[1]]
                            if gr_type == 1:
                                m[j][i[1]] = m[i[1]][j]
                            ans.append(way_to_vertice[i[1]] + ans[0][ans[0].index(j):])
                            num_of_ans -= 1
                            k += 1
                        elif (marked[j] == 1) & (ways[j] < ways[i[1]] + max_weight) & random.randint(0, 1):
                            m[i[1]][j] = random.randint(max(ways[j] - ways[i[1]] + 1, min_weight), max_weight)
                            if gr_type == 1:
                                m[j][i[1]] = m[i[1]][j]
                            k += 1
                        if k > min_edges:
                                break
            if num_of_ans > 0:
                flag_recount = 0
                continue

        if attempts == 10:
            fail = 1

        some_matrix = []

        for i in range(n-1):
            way_to_vertice[i] = [d + 1 for d in way_to_vertice[i]]
            some_matrix.append({'seq': way_to_vertice[i], 'len': ways[i]})

        for j in range(keeper):
            ans[j] = [p + 1 for p in ans[j]]

        outputs.append([{'m': m, 'ans': ans, 'way': ways[n-1], 'each_way': some_matrix}])

    return {'output': outputs, 'inf': inf, 'fail': fail, 'type': task_type}
# <sub> это нижний индекс
