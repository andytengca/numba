from __future__ import print_function, absolute_import
import numpy as np
from numbapro import vectorize
from numbapro import cuda, int32, float32, float64
from timeit import default_timer as time
from numbapro.testsupport import unittest

sig = [int32(int32, int32),
       float32(float32, float32),
       float64(float64, float64)]


@vectorize(sig, target='gpu')
def vector_add(a, b):
    return a + b


cuda_ufunc = vector_add

test_dtypes = np.float32, np.int32


class TestCUDAVectorize(unittest.TestCase):
    def test_1d(self):
        # build python ufunc
        np_ufunc = np.add

        # test it out
        def test(ty):
            print("Test %s" % ty)
            data = np.array(np.random.random(1e+6 + 1), dtype=ty)

            ts = time()
            result = cuda_ufunc(data, data)
            tnumba = time() - ts

            ts = time()
            gold = np_ufunc(data, data)
            tnumpy = time() - ts

            print("Numpy time: %fs" % tnumpy)
            print("Numba time: %fs" % tnumba)

            if tnumba < tnumpy:
                print("Numba is FASTER by %fx" % (tnumpy / tnumba))
            else:
                print("Numba is SLOWER by %fx" % (tnumba / tnumpy))

            self.assertTrue(np.allclose(gold, result), (gold, result))

        test(np.double)
        test(np.float32)
        test(np.int32)

    def test_1d_async(self):
        # build python ufunc
        np_ufunc = np.add

        # test it out
        def test(ty):
            print("Test %s" % ty)
            data = np.array(np.random.random(1e+6 + 1), dtype=ty)

            ts = time()
            stream = cuda.stream()
            device_data = cuda.to_device(data, stream)
            dresult = cuda_ufunc(device_data, device_data, stream=stream)
            result = dresult.copy_to_host()
            stream.synchronize()
            tnumba = time() - ts

            ts = time()
            gold = np_ufunc(data, data)
            tnumpy = time() - ts

            print("Numpy time: %fs" % tnumpy)
            print("Numba time: %fs" % tnumba)

            if tnumba < tnumpy:
                print("Numba is FASTER by %fx" % (tnumpy / tnumba))
            else:
                print("Numba is SLOWER by %fx" % (tnumba / tnumpy))

            self.assertTrue(np.allclose(gold, result), (gold, result))

        test(np.double)
        test(np.float32)
        test(np.int32)

    def test_nd(self):
        def test(dtype, order, nd, size=4):
            data = np.random.random((size,) * nd).astype(dtype)
            data[data != data] = 2.4
            data[data == float('inf')] = 3.8
            data[data == float('-inf')] = -3.8
            data2 = np.array(data.T, order=order) #.copy(order=order)

            result = data + data2
            our_result = cuda_ufunc(data, data2)
            self.assertTrue(np.allclose(result, our_result),
                            (dtype, order, result, our_result))

        for nd in range(1, 8):
            for dtype in test_dtypes:
                for order in ('C', 'F'):
                    test(dtype, order, nd)

    def test_ufunc_attrib(self):
        self.reduce_test(8)
        self.reduce_test(100)
        self.reduce_test(2 ** 10 + 1)
        self.reduce_test2(8)
        self.reduce_test2(100)
        self.reduce_test2(2 ** 10 + 1)

    def test_output_arg(self):
        A = np.arange(10, dtype=np.float32)
        B = np.arange(10, dtype=np.float32)
        C = np.empty_like(A)
        vector_add(A, B, out=C)
        self.assertTrue(np.allclose(A + B, C))

    def reduce_test(self, n):
        x = np.arange(n, dtype=np.int32)
        gold = np.add.reduce(x)
        result = cuda_ufunc.reduce(x)
        self.assertTrue(result == gold, (result, gold))

    def reduce_test2(self, n):
        x = np.arange(n, dtype=np.int32)
        gold = np.add.reduce(x)
        stream = cuda.stream()
        dx = cuda.to_device(x, stream)
        result = cuda_ufunc.reduce(dx, stream=stream)
        self.assertTrue(result == gold, (result, gold))


if __name__ == '__main__':
    unittest.main()