// Full-width photo banners at the top of a page, directly under the header.
// Photos are 2560 x 1440 (16:9). `pos` is the focal point used when the photo is cropped (phones);
// `phoneRatio` is the crop shape on phones (width / height).
export interface Banner { src: string; alt: string; pos: string; phoneRatio: string }

export const banners: Record<string, Banner> = {
  blog: {
    src: '/images/banner-blog.jpg',
    alt: 'A man in round glasses, his head seen from above, emerging from a pile of papers covered in handwriting on a wooden floor',
    pos: '40% 50%',
    phoneRatio: '3 / 4',
  },
};
