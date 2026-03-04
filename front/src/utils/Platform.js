const getPlatform = () => {
    const ua = navigator.userAgent.toLowerCase();

    if (ua.includes('mac')) return 'macos';
    if (ua.includes('linux')) return 'linux';
    if (ua.includes('android')) return 'android';
    if (ua.includes('iphone') || ua.includes('ipad') || ua.includes('ipod')) return 'ios';
    if (ua.includes('win')) return 'windows';

    return 'unknown';
};

export default {
    is(platform) {
        if (!platform) return false;
        return platform === getPlatform();
    },

    in(platforms = []) {
        return platforms.includes(getPlatform());
    }
};