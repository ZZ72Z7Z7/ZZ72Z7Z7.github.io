import { defineCollection, reference } from 'astro:content';
import { glob } from 'astro/loaders';
import { z } from 'astro/zod';

// Text fields come in pairs: the English field, and the same name + "_it".
// Dates, places, images and links are shared by both languages.

const pages = defineCollection({
  loader: glob({ base: './src/content/pages', pattern: '**/*.md' }),
  schema: z.object({
    title: z.string(),
    description: z.string().optional(),
    translation: z.string().optional(), // "draft" on Italian pages drafted by Claude: they need human review before launch (see ITALIAN-REVIEW.md)
  }),
});

const workshops = defineCollection({
  loader: glob({ base: './src/content/workshops', pattern: '**/*.md' }),
  schema: z.object({
    title: z.string(),
    title_it: z.string().optional(),
    subtitle: z.string().optional(),
    subtitle_it: z.string().optional(),
    image: z.string().optional(), // the primary picture: shown on the workshop page and as the thumbnail in the Workshops list
    image_caption: z.string().optional(),
    image_caption_it: z.string().optional(),
    program_it: z.string().optional(),
    credits_it: z.string().optional(),
    translation: z.string().optional(),
    program: z.string().optional(), // the "Program" section, only for workshops that have one
    accordion_desktop: z.boolean().optional(), // experiment: keep the accordion rows on desktop too
    gallery: z.array(z.object({ src: z.string(), caption: z.string().optional(), caption_it: z.string().optional() })).optional(), // the other pictures
    credits: z.string().optional(), // photo credits, shown under the gallery
    // The body of the file is the English description; body_it is the Italian one.
    body_it: z.string().optional(),
  }),
});

const schedule = defineCollection({
  loader: glob({ base: './src/content/schedule', pattern: '**/*.yml' }),
  schema: z.object({
    workshop: reference('workshops').optional(),
    title: z.string().optional(),
    title_it: z.string().optional(),
    start: z.coerce.date(),
    end: z.coerce.date().optional(),
    extra_dates: z.string().optional(),
    extra_dates_it: z.string().optional(),
    city: z.string().optional(),
    region: z.string().optional(), // state or province, shown between city and country
    country: z.string().optional(),
    venue: z.string().optional(),
    // practical information of this edition, shown on the workshop page (rich text each)
    schedule: z.string().optional(),
    location_details: z.string().optional(),
    tuition: z.string().optional(),
    language: z.string().optional(),
    travel: z.string().optional(),
    accommodation: z.string().optional(),
    applications: z.string().optional(),
    schedule_it: z.string().optional(),
    location_details_it: z.string().optional(),
    tuition_it: z.string().optional(),
    language_it: z.string().optional(),
    travel_it: z.string().optional(),
    accommodation_it: z.string().optional(),
    applications_it: z.string().optional(),
    translation: z.string().optional(),
    taught_with: z.string().optional(),
    collaboration_name: z.string().optional(),
    collaboration_url: z.string().optional(),
    language_note: z.string().optional(),
    language_note_it: z.string().optional(),
    // application status chip (261011): shown only while the edition is upcoming; an Open edition turns Closed by itself after applications_close
    status: z.enum(['pending', 'open', 'waitlist', 'closed']).optional(),
    applications_open: z.coerce.date().optional(),  // Pending: when applications open (empty = TBA)
    applications_close: z.coerce.date().optional(), // Open: the application deadline
    external_link: z.string().optional(),
    image: z.string().optional(), // thumbnail shown beside the entry on the Workshops page
    description: z.string().optional(), // short description shown under the title on the Workshops page
    description_it: z.string().optional(),
  }),
});

const events = defineCollection({
  loader: glob({ base: './src/content/events', pattern: '**/*.md' }),
  schema: z.object({
    title: z.string(),
    title_it: z.string().optional(),
    subtitle: z.string().optional(),
    subtitle_it: z.string().optional(),
    start: z.coerce.date(),
    time: z.string().optional(),
    end: z.coerce.date().optional(),
    city: z.string().optional(),
    country: z.string().optional(),
    venue: z.string().optional(),
    address: z.string().optional(),
    image: z.string().optional(),
    admission: z.string().optional(),
    admission_it: z.string().optional(),
    booking_link: z.string().optional(),
    booking_email: z.string().optional(),
    pdfs: z
      .array(z.object({ label: z.string(), label_it: z.string().optional(), file: z.string() }))
      .optional(),
    body_it: z.string().optional(),
    translation: z.string().optional(),
  }),
});

const blog = defineCollection({
  loader: glob({ base: './src/content/blog', pattern: '**/*.md' }),
  schema: z.object({
    title: z.string(),
    title_it: z.string().optional(),
    date: z.coerce.date(),
    category: z.enum(['Pedagogy', 'Poetry', 'Philosophy']),
    image: z.string().optional(),
    audio: z.string().optional(),
    body_it: z.string().optional(),
    translation: z.string().optional(),
  }),
});

export const collections = { pages, workshops, schedule, events, blog };
