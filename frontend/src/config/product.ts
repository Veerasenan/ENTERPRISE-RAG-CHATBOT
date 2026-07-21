export const PRODUCT_NAME = "PolicyHub";

export const PRODUCT_TAGLINE = "Rules & Guidance";

const _words = PRODUCT_NAME.split(/\s+/).filter(Boolean);
let _initials = "";
if (_words.length === 1) {
	const w = _words[0];
	const caps = w.match(/[A-Z]/g) || [];
	if (caps.length >= 2) {
		_initials = caps.slice(0, 2).join("");
	} else if (caps.length === 1) {
		if (caps[0] !== w[0]) {
			_initials = (w[0] + caps[0]).slice(0, 2);
		} else {
			_initials = (w[0] + (w[1] || "")).slice(0, 2);
		}
	} else {
		_initials = w.slice(0, 2);
	}
} else {
	_initials = _words.map((p) => p[0]).slice(0, 2).join("");
}

export const PRODUCT_INITIALS = _initials.toUpperCase();
