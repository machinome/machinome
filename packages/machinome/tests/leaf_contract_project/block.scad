module block(size = 8) {
	difference() {
		cube(size, center = true);
		cylinder(h = size * 2, r = size / 4, center = true);
	}
}
