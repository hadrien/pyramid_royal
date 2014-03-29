Changelog
=========

Development
-----------

- Breaking changes: query params are not anymore passed to resources methods
  via ``**kwargs`` but as a ``dict``.
- Add ``renderer_adapter`` decorator to register adapter via ``config.scan``.
- Add renderer adapter to configuration introspectables under *Renderer
  adapters* category.

0.6
---

- Breaking changes: TBD
- Move onctuous away in favor of voluptuous
- Added method tunneling to permit ``PUT``, and ``DELETE`` via ``POST``
  methods.
- TBD: adapt how request body is parsed.


0.5.1
-----

- Add Base.__getitem__ which gets children from self.children

0.5
---

- Breaking change: Pages parameters are not anymore page & page_size but offset
  and limit. It is more developer and db friendly.

0.2
---

- onctuous schema checking on resource creation.

0.1
---

- Initial version
- royal renderer able to return bson or json.
- royal.includeme adds royal renderer and views.
- royal.resource.PaginatedResult which permits Collection.index to return
  paginated results.
- royal.views with default views for Collection and Resource.
- CollectionView.index does automatic pagination.
