function getPlatform () {
    const { platform } = window.navigator

    if (platform.indexOf('Mac') === 0) return 'macos'

    if (platform.indexOf('Linux') === 0) return 'linux'

    if (platform.indexOf('Android') === 0) return 'android'

    if (
        platform.indexOf('iPhone') ||
        platform.indexOf('iPad') ||
        platform.indexOf('iPod')
    ) return 'ios'

    return 'windows'
}

export default {
    is (platform) {
        if (!platform) return false

        return platform === getPlatform()
    },

    in (platforms = []) {
        return platforms.includes(getPlatform())
    }
}
