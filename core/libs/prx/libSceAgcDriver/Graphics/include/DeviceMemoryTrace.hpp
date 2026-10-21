#pragma once
#include <vulkan/vulkan.h>
#include <algorithm>
#include <chrono>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <mutex>
#include <unordered_map>
#include <vector>

namespace AgcDriver::Graphics::DeviceMemoryTrace {

struct Site {
    std::int64_t live = 0;
    std::uint64_t allocations = 0;
};

struct State {
    std::mutex mutex;
    PFN_vkAllocateMemory allocate = nullptr;
    PFN_vkFreeMemory free = nullptr;
    std::unordered_map<std::uintptr_t, Site> sites;
    std::unordered_map<VkDeviceMemory, std::pair<std::uintptr_t, VkDeviceSize>> memories;
    std::chrono::steady_clock::time_point printed = std::chrono::steady_clock::now();
};

inline bool Enabled() {
    static const bool enabled = std::getenv("APS5_TRACE_DEVICE_MEMORY") != nullptr;
    return enabled;
}

inline State& Get() {
    static State state;
    return state;
}

inline void printLocked(State& state) {
    const auto now = std::chrono::steady_clock::now();
    if (now - state.printed < std::chrono::seconds(10)) return;
    state.printed = now;
    std::vector<std::pair<std::uintptr_t, Site>> sorted(state.sites.begin(), state.sites.end());
    std::sort(sorted.begin(), sorted.end(), [](const auto& a, const auto& b) { return a.second.live > b.second.live; });
    std::int64_t total = 0;
    for (const auto& entry : sorted) total += entry.second.live;
    std::fprintf(stderr, "[devmem] live %lld MiB in %zu allocations\n", static_cast<long long>(total >> 20), state.memories.size());
    for (std::size_t i = 0; i < std::min<std::size_t>(sorted.size(), 12); ++i) std::fprintf(stderr, "[devmem]   site 0x%llx type %u live %lld MiB, %llu allocations\n", static_cast<unsigned long long>(sorted[i].first >> 8u), static_cast<unsigned>(sorted[i].first & 0xffu), static_cast<long long>(sorted[i].second.live >> 20), static_cast<unsigned long long>(sorted[i].second.allocations));
}

[[gnu::noinline]] inline VkResult VKAPI_CALL Allocate(VkDevice device, const VkMemoryAllocateInfo* info, const VkAllocationCallbacks* callbacks, VkDeviceMemory* memory) {
    const auto site = (reinterpret_cast<std::uintptr_t>(__builtin_return_address(0)) << 8u) | info->memoryTypeIndex;
    auto& state = Get();
    const auto result = state.allocate(device, info, callbacks, memory);
    if (result != VK_SUCCESS) return result;
    std::lock_guard lock(state.mutex);
    auto& entry = state.sites[site];
    entry.live += static_cast<std::int64_t>(info->allocationSize);
    ++entry.allocations;
    state.memories[*memory] = {site, info->allocationSize};
    printLocked(state);
    return result;
}

[[gnu::noinline]] inline void VKAPI_CALL Free(VkDevice device, VkDeviceMemory memory, const VkAllocationCallbacks* callbacks) {
    auto& state = Get();
    {
        std::lock_guard lock(state.mutex);
        if (const auto found = state.memories.find(memory); found != state.memories.end()) {
            state.sites[found->second.first].live -= static_cast<std::int64_t>(found->second.second);
            state.memories.erase(found);
        }
    }
    state.free(device, memory, callbacks);
}

inline PFN_vkVoidFunction Wrap(const char* name, PFN_vkVoidFunction function) {
    if (!Enabled() || function == nullptr) return function;
    auto& state = Get();
    if (std::strcmp(name, "vkAllocateMemory") == 0) {
        state.allocate = reinterpret_cast<PFN_vkAllocateMemory>(function);
        return reinterpret_cast<PFN_vkVoidFunction>(&Allocate);
    }
    if (std::strcmp(name, "vkFreeMemory") == 0) {
        state.free = reinterpret_cast<PFN_vkFreeMemory>(function);
        return reinterpret_cast<PFN_vkVoidFunction>(&Free);
    }
    return function;
}

}
