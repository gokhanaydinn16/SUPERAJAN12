use std::fs;
use std::path::Path;

const ICON_SIZE: usize = 256;

fn main() {
    ensure_release_icon_assets();
    tauri_build::build()
}

fn ensure_release_icon_assets() {
    let generated_dir = Path::new("icons/generated");
    let _ = fs::create_dir_all(generated_dir);

    let rgba = render_icon(ICON_SIZE);
    let png_bytes = write_png(ICON_SIZE as u32, ICON_SIZE as u32, &rgba);

    write_icon(generated_dir.join("icon.png"), &png_bytes);
    write_icon(generated_dir.join("icon.ico"), &write_ico(&png_bytes));
}

fn write_icon(path: impl AsRef<Path>, bytes: &[u8]) {
    fs::write(path, bytes).expect("failed to write generated icon asset");
}

fn render_icon(size: usize) -> Vec<u8> {
    let mut pixels = vec![0u8; size * size * 4];
    let radius = size as f32 * 0.19;
    let stroke = size as f32 * 0.052;
    let accent = size as f32 * 0.046;

    let shield = [
        point(size, 64.0, 26.0),
        point(size, 91.0, 38.0),
        point(size, 91.0, 62.0),
        point(size, 64.0, 102.0),
        point(size, 37.0, 62.0),
        point(size, 37.0, 38.0),
    ];
    let accent_points = [
        point(size, 49.0, 69.0),
        point(size, 61.0, 69.0),
        point(size, 67.0, 42.0),
        point(size, 79.0, 59.0),
        point(size, 89.0, 59.0),
    ];

    for y in 0..size {
        for x in 0..size {
            let px = x as f32 + 0.5;
            let py = y as f32 + 0.5;
            let base = (y * size + x) * 4;

            let rect_alpha = rounded_rect_alpha(px, py, size as f32, radius);
            if rect_alpha <= 0.0 {
                continue;
            }

            let t = ((px + py) / (2.0 * size as f32)).clamp(0.0, 1.0);
            let bg = mix([15.0, 23.0, 42.0], [14.0, 165.0, 233.0], t);
            blend(&mut pixels[base..base + 4], bg, rect_alpha);

            let shield_alpha = polyline_alpha(px, py, &shield, stroke, true);
            if shield_alpha > 0.0 {
                blend(&mut pixels[base..base + 4], [226.0, 232.0, 240.0], shield_alpha);
            }

            let accent_alpha = polyline_alpha(px, py, &accent_points, accent, false);
            if accent_alpha > 0.0 {
                let at = (px / size as f32).clamp(0.0, 1.0);
                let accent_rgb = mix([34.0, 197.0, 94.0], [56.0, 189.0, 248.0], at);
                blend(&mut pixels[base..base + 4], accent_rgb, accent_alpha);
            }
        }
    }

    pixels
}

fn point(size: usize, x: f32, y: f32) -> [f32; 2] {
    let scale = size as f32 / 128.0;
    [x * scale, y * scale]
}

fn rounded_rect_alpha(px: f32, py: f32, size: f32, radius: f32) -> f32 {
    let cx = size * 0.5;
    let cy = size * 0.5;
    let qx = (px - cx).abs() - (size * 0.5 - radius);
    let qy = (py - cy).abs() - (size * 0.5 - radius);
    let ox = qx.max(0.0);
    let oy = qy.max(0.0);
    let outside = (ox * ox + oy * oy).sqrt();
    let inside = qx.max(qy).min(0.0);
    coverage_from_signed_distance(outside + inside)
}

fn polyline_alpha(px: f32, py: f32, points: &[[f32; 2]], width: f32, closed: bool) -> f32 {
    let mut best: f32 = 0.0;
    for window in points.windows(2) {
        best = best.max(segment_alpha(px, py, window[0], window[1], width));
    }
    if closed {
        best = best.max(segment_alpha(px, py, points[points.len() - 1], points[0], width));
    }
    best
}

fn segment_alpha(px: f32, py: f32, a: [f32; 2], b: [f32; 2], width: f32) -> f32 {
    let vx = b[0] - a[0];
    let vy = b[1] - a[1];
    let wx = px - a[0];
    let wy = py - a[1];
    let c1 = wx * vx + wy * vy;
    let c2 = vx * vx + vy * vy;
    let t = if c2 <= f32::EPSILON { 0.0 } else { (c1 / c2).clamp(0.0, 1.0) };
    let dx = px - (a[0] + t * vx);
    let dy = py - (a[1] + t * vy);
    let distance = (dx * dx + dy * dy).sqrt();
    coverage_from_signed_distance(distance - width * 0.5)
}

fn coverage_from_signed_distance(distance: f32) -> f32 {
    if distance <= 0.0 {
        1.0
    } else {
        (1.0 - distance).clamp(0.0, 1.0)
    }
}

fn mix(start: [f32; 3], end: [f32; 3], t: f32) -> [f32; 3] {
    [
        start[0] + (end[0] - start[0]) * t,
        start[1] + (end[1] - start[1]) * t,
        start[2] + (end[2] - start[2]) * t,
    ]
}

fn blend(pixel: &mut [u8], rgb: [f32; 3], alpha: f32) {
    let src_a = alpha.clamp(0.0, 1.0);
    let dst_a = pixel[3] as f32 / 255.0;
    let out_a = src_a + dst_a * (1.0 - src_a);
    if out_a <= f32::EPSILON {
        return;
    }

    for (channel, src) in rgb.into_iter().enumerate() {
        let dst = pixel[channel] as f32 / 255.0;
        let out = (src / 255.0 * src_a + dst * dst_a * (1.0 - src_a)) / out_a;
        pixel[channel] = (out.clamp(0.0, 1.0) * 255.0).round() as u8;
    }
    pixel[3] = (out_a * 255.0).round() as u8;
}

fn write_png(width: u32, height: u32, rgba: &[u8]) -> Vec<u8> {
    let mut raw = Vec::with_capacity((width as usize * 4 + 1) * height as usize);
    for row in rgba.chunks_exact(width as usize * 4) {
        raw.push(0);
        raw.extend_from_slice(row);
    }

    let compressed = zlib_store(&raw);
    let mut png = Vec::new();
    png.extend_from_slice(&[137, 80, 78, 71, 13, 10, 26, 10]);

    let mut ihdr = Vec::with_capacity(13);
    ihdr.extend_from_slice(&width.to_be_bytes());
    ihdr.extend_from_slice(&height.to_be_bytes());
    ihdr.extend_from_slice(&[8, 6, 0, 0, 0]);
    write_chunk(&mut png, *b"IHDR", &ihdr);
    write_chunk(&mut png, *b"IDAT", &compressed);
    write_chunk(&mut png, *b"IEND", &[]);
    png
}

fn write_chunk(png: &mut Vec<u8>, kind: [u8; 4], data: &[u8]) {
    png.extend_from_slice(&(data.len() as u32).to_be_bytes());
    png.extend_from_slice(&kind);
    png.extend_from_slice(data);

    let mut crc_input = Vec::with_capacity(kind.len() + data.len());
    crc_input.extend_from_slice(&kind);
    crc_input.extend_from_slice(data);
    png.extend_from_slice(&crc32(&crc_input).to_be_bytes());
}

fn zlib_store(data: &[u8]) -> Vec<u8> {
    let mut out = vec![0x78, 0x01];
    let mut remaining = data;
    while !remaining.is_empty() {
        let chunk_len = remaining.len().min(65_535);
        let final_flag = if chunk_len == remaining.len() { 1u8 } else { 0u8 };
        out.push(final_flag);
        out.extend_from_slice(&(chunk_len as u16).to_le_bytes());
        out.extend_from_slice((!(chunk_len as u16)).to_le_bytes().as_slice());
        out.extend_from_slice(&remaining[..chunk_len]);
        remaining = &remaining[chunk_len..];
    }
    out.extend_from_slice(&adler32(data).to_be_bytes());
    out
}

fn adler32(data: &[u8]) -> u32 {
    let mut s1 = 1u32;
    let mut s2 = 0u32;
    for &byte in data {
        s1 = (s1 + byte as u32) % 65_521;
        s2 = (s2 + s1) % 65_521;
    }
    (s2 << 16) | s1
}

fn crc32(data: &[u8]) -> u32 {
    let mut crc = 0xffff_ffffu32;
    for &byte in data {
        crc ^= byte as u32;
        for _ in 0..8 {
            let mask = (crc & 1).wrapping_neg() & 0xedb8_8320;
            crc = (crc >> 1) ^ mask;
        }
    }
    !crc
}

fn write_ico(png_bytes: &[u8]) -> Vec<u8> {
    let mut ico = Vec::with_capacity(6 + 16 + png_bytes.len());
    ico.extend_from_slice(&0u16.to_le_bytes());
    ico.extend_from_slice(&1u16.to_le_bytes());
    ico.extend_from_slice(&1u16.to_le_bytes());
    ico.push(0);
    ico.push(0);
    ico.push(0);
    ico.push(0);
    ico.extend_from_slice(&1u16.to_le_bytes());
    ico.extend_from_slice(&32u16.to_le_bytes());
    ico.extend_from_slice(&(png_bytes.len() as u32).to_le_bytes());
    ico.extend_from_slice(&(6u32 + 16u32).to_le_bytes());
    ico.extend_from_slice(png_bytes);
    ico
}
