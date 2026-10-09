create extension if not exists pg_trgm;
create index if not exists rounds_name_trgm_idx on rounds using gin (round_name gin_trgm_ops);

create or replace function find_similar_entities(
    p_entity_type text,
    p_normalized_value text,
    p_limit integer default 10
)
returns table (
    entity_id uuid,
    canonical_name text,
    normalized_value text,
    category text,
    topic text,
    subtopic text,
    difficulty text
)
language plpgsql
stable
as $$
declare
    candidate_limit integer := greatest(1, least(coalesce(p_limit, 10), 50));
begin
    case p_entity_type
        when 'COMPANY' then
            return query
            select c.id, c.name, c.normalized_name, null::text, null::text, null::text, null::text
            from companies c
            where c.name % p_normalized_value
            order by similarity(c.name, p_normalized_value) desc
            limit candidate_limit;
        when 'ROLE' then
            return query
            select r.id, r.name, r.normalized_name, null::text, null::text, null::text, null::text
            from roles r
            where r.name % p_normalized_value
            order by similarity(r.name, p_normalized_value) desc
            limit candidate_limit;
        when 'ROUND' then
            return query
            select r.id, r.round_name, lower(r.round_name), null::text, null::text, null::text, null::text
            from rounds r
            where r.round_name % p_normalized_value
            order by similarity(r.round_name, p_normalized_value) desc
            limit candidate_limit;
        when 'QUESTION' then
            return query
            select q.id, q.canonical_text, q.normalized_text, q.category, q.topic, q.subtopic, q.difficulty
            from question_canonical q
            where q.canonical_text % p_normalized_value
            order by similarity(q.canonical_text, p_normalized_value) desc
            limit candidate_limit;
        else
            return;
    end case;
end;
$$;
