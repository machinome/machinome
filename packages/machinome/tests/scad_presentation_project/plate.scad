module plate(width = 10) {
	difference() {
		cube([width, width, 2], center = true);
		cylinder(h = 4, r = width / 5, center = true);
	}
}
