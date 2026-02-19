// Custom REST API: /wp-json/custom/v1/seo-score/{id}
// RankMath 점수를 서버사이드에서 계산하고 rank_math_seo_score에 저장
add_action('rest_api_init', function() {
    register_rest_route('custom/v1', '/seo-score/(?P<id>\d+)', array(
        'methods' => 'GET',
        'callback' => 'custom_compute_seo_score',
        'permission_callback' => function() {
            return current_user_can('edit_posts');
        },
    ));
});

function custom_compute_seo_score($request) {
    $post_id = (int) $request['id'];
    $post = get_post($post_id);
    if (!$post) return new WP_Error('not_found', 'Post not found', array('status' => 404));

    $title = $post->post_title;
    $content = wp_strip_all_tags($post->post_content);
    $slug = $post->post_name;
    $focus_kw = mb_strtolower(get_post_meta($post_id, 'rank_math_focus_keyword', true));
    $seo_title = get_post_meta($post_id, 'rank_math_title', true);
    $description = get_post_meta($post_id, 'rank_math_description', true);

    if (!$focus_kw) {
        return array('post_id' => $post_id, 'score' => 0, 'error' => 'No focus keyword set');
    }

    $score = 0;
    $max = 0;
    $checks = array();

    $do_check = function($name, $passed, $weight = 1) use (&$score, &$max, &$checks) {
        $max += $weight;
        if ($passed) $score += $weight;
        $checks[] = array('name' => $name, 'passed' => $passed, 'weight' => $weight);
    };

    $content_lower = mb_strtolower($content);
    $char_count = mb_strlen($content);

    // 기본 SEO
    $do_check('keyword_in_seo_title', $seo_title && mb_stripos($seo_title, $focus_kw) !== false, 2);
    $do_check('keyword_in_meta_desc', $description && mb_stripos($description, $focus_kw) !== false, 2);
    $do_check('keyword_in_url', mb_stripos(urldecode($slug), str_replace(' ', '-', $focus_kw)) !== false || mb_stripos(urldecode($slug), $focus_kw) !== false, 2);

    $first_10pct = mb_substr($content_lower, 0, max((int)($char_count * 0.1), 200));
    $do_check('keyword_in_intro', mb_stripos($first_10pct, $focus_kw) !== false, 2);
    $do_check('content_length', $char_count >= 2500, 2);
    $do_check('keyword_in_content', mb_stripos($content_lower, $focus_kw) !== false, 1);

    // 추가 SEO
    preg_match_all('/<h[2-4][^>]*>(.*?)<\/h[2-4]>/si', $post->post_content, $h_matches);
    $h_with_kw = 0;
    if (!empty($h_matches[1])) {
        foreach ($h_matches[1] as $h) {
            if (mb_stripos(wp_strip_all_tags($h), $focus_kw) !== false) $h_with_kw++;
        }
    }
    $do_check('keyword_in_headings', $h_with_kw >= 1, 2);

    $kw_count = mb_substr_count($content_lower, $focus_kw);
    $kw_len = mb_strlen($focus_kw);
    $density = $char_count > 0 ? ($kw_count * $kw_len / $char_count * 100) : 0;
    $do_check('keyword_density', $density >= 0.5 && $density <= 2.5, 2);

    preg_match_all('/<img[^>]*>/i', $post->post_content, $img_matches);
    $do_check('has_images', count($img_matches[0]) > 0, 1);

    $do_check('url_length', mb_strlen($slug) <= 75, 1);

    preg_match_all('/href=["\']https?:\/\/pearsoninsight\.com[^"\']*["\']/i', $post->post_content, $int_links);
    $do_check('internal_links', count($int_links[0]) >= 1, 2);

    preg_match_all('/href=["\']https?:\/\/(?!pearsoninsight\.com)[^"\']+["\']/i', $post->post_content, $ext_links);
    $do_check('external_links', count($ext_links[0]) >= 1, 1);

    // 제목 가독성
    if ($seo_title) {
        $do_check('title_length', mb_strlen($seo_title) <= 60, 1);
        $do_check('title_starts_with_kw', mb_stripos($seo_title, $focus_kw) === 0, 1);
        $do_check('title_has_number', (bool) preg_match('/\d/', $seo_title), 1);
    } else {
        $do_check('seo_title_set', false, 1);
    }

    // 메타 설명
    if ($description) {
        $md_len = mb_strlen($description);
        $do_check('meta_desc_length', $md_len >= 120 && $md_len <= 160, 1);
    }

    // 단락 길이
    preg_match_all('/<p[^>]*>(.*?)<\/p>/si', $post->post_content, $p_matches);
    $long_p = 0;
    foreach ($p_matches[1] as $p) {
        if (mb_strlen(wp_strip_all_tags($p)) > 300) $long_p++;
    }
    $do_check('short_paragraphs', $long_p === 0, 1);

    $do_check('faq_schema', mb_stripos($post->post_content, 'FAQPage') !== false, 1);

    preg_match_all('/<h2[^>]*>/i', $post->post_content, $h2_matches);
    $h2_count = count($h2_matches[0]);
    $do_check('h2_structure', $h2_count >= 3 && $h2_count <= 8, 1);

    $pct = $max > 0 ? round($score / $max * 100) : 0;

    // rank_math_seo_score에 저장
    update_post_meta($post_id, 'rank_math_seo_score', (string) $pct);

    return array(
        'post_id' => $post_id,
        'score' => $pct,
        'passed' => $score,
        'total' => $max,
        'checks' => $checks,
        'density' => round($density, 2),
    );
}
