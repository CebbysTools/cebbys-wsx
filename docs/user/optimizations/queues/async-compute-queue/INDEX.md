# Async compute queue

Status: `researched`

## Cause

Shader 0x115258a000 runs on a PS5 compute queue, but on the PC it uses the single Vulkan queue. Each run blocks graphics for about 340 ms.

## Options

| Option | Pros | Cons |
|---|---|---|
| Second recorder and second `VkQueue` for compute-only PS5 queues | Graphics continues. | Hazard tracking across recorders. Labels and `WAIT_REG_MEM` as timeline semaphores. |
| Keep one queue | Simple. Correct. | Graphics waits. |

## Result

Not implemented. The device already asks for two queues when the family has them.

## Why

Planned after the CPU-GPU sync work, because the cross-queue rules depend on it.
