{
  "responses": {
    "r1": {
      "findings": [
        {
          "file": "src/google/adk/optimization/local_eval_sampler.py",
          "line_start": 292,
          "line_end": 292,
          "category": "logic",
          "description": "Removed null check allows NoneType.round() to fail if eval_metric_result.score is None.",
          "confidence": 0.95
        }
      ]
    },
    "r2": {
      "findings": [
        {
          "file": "coremltools/converters/mil/frontend/torch/ops.py",
          "line_start": 5657,
          "line_end": 5657,
          "category": "logic",
          "description": "Simplified logic loses overflow detection and clamping of rand_int to high-1 range.",
          "confidence": 0.92
        }
      ]
    },
    "r3": {
      "findings": [
        {
          "file": "coremltools/converters/mil/mil/ops/defs/iOS15/normalization.py",
          "line_start": 294,
          "line_end": 294,
          "category": "logic",
          "description": "Copy-paste error checks gamma.shape instead of beta.shape for beta validation.",
          "confidence": 0.99
        }
      ]
    },
    "r4": {
      "findings": [
        {
          "file": "core/src/main/java/com/google/errorprone/bugpatterns/threadsafety/ConstantExpressions.java",
          "line_start": 201,
          "line_end": 201,
          "category": "logic",
          "description": "Removed @Nullable allows NPE if object is null; toString() called without null check.",
          "confidence": 0.93
        }
      ]
    },
    "r5": {
      "findings": [
        {
          "file": "swift/Sources/FlatBuffers/Verifiable.swift",
          "line_start": 61,
          "line_end": 61,
          "category": "logic",
          "description": "Removed overflow check for multiplication; passing intLen instead of byteCount skips size validation.",
          "confidence": 0.94
        }
      ]
    },
    "r6": {
      "findings": [
        {
          "file": "github/github.go",
          "line_start": 1391,
          "line_end": 1394,
          "category": "security",
          "description": "Removed redaction for access_token and token parameters; now only redacts client_secret.",
          "confidence": 0.96
        }
      ]
    },
    "r7": {
      "findings": []
    },
    "r8": {
      "findings": []
    },
    "r9": {
      "findings": [
        {
          "file": "pkl-core/src/main/java/org/pkl/core/stdlib/base/IntNodes.java",
          "line_start": 193,
          "line_end": 193,
          "category": "logic",
          "description": "Changed logic negates the sign but applies abs() causing incorrect radix conversion for negative numbers.",
          "confidence": 0.90
        }
      ]
    },
    "r10": {
      "findings": [
        {
          "file": "request.go",
          "line_start": 108,
          "line_end": 108,
          "category": "logic",
          "description": "Returns bytesRead without adding len(encodedReq), losing partial read count on error.",
          "confidence": 0.93
        }
      ]
    },
    "r11": {
      "findings": [
        {
          "file": "metadata_request.go",
          "line_start": 34,
          "line_end": 34,
          "category": "logic",
          "description": "Duplicate version check for V2_4_0_0 makes the V2_3_0_0 branch unreachable.",
          "confidence": 0.98
        }
      ]
    },
    "r12": {
      "findings": [
        {
          "file": "servicetalk-buffer-api/src/main/java/io/servicetalk/buffer/api/AbstractBuffer.java",
          "line_start": 134,
          "line_end": 134,
          "category": "logic",
          "description": "Mask changed from 0xffff to 0xfff loses one bit; getUnsignedShort will not correctly zero-extend short to int.",
          "confidence": 0.99
        }
      ]
    },
    "r13": {
      "findings": [
        {
          "file": "servicetalk-concurrent-api/src/main/java/io/servicetalk/concurrent/api/FromInputStreamPublisher.java",
          "line_start": 205,
          "line_end": 205,
          "category": "logic",
          "description": "Removed overflow protection allows available + 1 to overflow if available is Integer.MAX_VALUE.",
          "confidence": 0.88
        }
      ]
    },
    "r14": {
      "findings": [
        {
          "file": "servicetalk-loadbalancer/src/main/java/io/servicetalk/loadbalancer/RoundRobinSelector.java",
          "line_start": 200,
          "line_end": 200,
          "category": "logic",
          "description": "Operator precedence error: (int) counter % hostsSize casts counter to int before modulo instead of after.",
          "confidence": 0.97
        }
      ]
    },
    "r15": {
      "findings": [
        {
          "file": "Sources/SortedCollections/BTree/_BTree.swift",
          "line_start": 34,
          "line_end": 34,
          "category": "logic",
          "description": "Changed max to min reverses capacity logic; now returns minimum instead of maximum capacity.",
          "confidence": 0.96
        },
        {
          "file": "Sources/SortedCollections/BTree/_BTree.swift",
          "line_start": 46,
          "line_end": 46,
          "category": "logic",
          "description": "Changed max to min reverses capacity logic; now returns minimum instead of maximum capacity.",
          "confidence": 0.96
        }
      ]
    },
    "r16": {
      "findings": [
        {
          "file": "lib/common/threading.c",
          "line_start": 146,
          "line_end": 146,
          "category": "logic",
          "description": "Removed cleanup code leaks allocated mutex if pthread_mutex_init fails.",
          "confidence": 0.97
        },
        {
          "file": "lib/common/threading.c",
          "line_start": 166,
          "line_end": 166,
          "category": "logic",
          "description": "Removed cleanup code leaks allocated cond if pthread_cond_init fails.",
          "confidence": 0.97
        }
      ]
    },
    "r17": {
      "findings": [
        {
          "file": "lib/compress/zstd_ldm.c",
          "line_start": 155,
          "line_end": 155,
          "category": "logic",
          "description": "Removed guard allows params->windowLog - params->hashRateLog to be negative when windowLog <= hashRateLog.",
          "confidence": 0.91
        }
      ]
    }
  }
}