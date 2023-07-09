# bucket sort function without comments

def bucket_sort(arr):
    buckets = [[_] for _ in range(10)]
    for num in arr:
        buckets[num].append(num)
    return [num for bucket in buckets for num in bucket]
