#ifndef SECURE_STRING_HXX
#define SECURE_STRING_HXX

#define GCR_API_SUBJECT_TO_CHANGE
#include <gcr/gcr.h>

template <class T> class secure_allocator
{
public:
	typedef T value_type;
	typedef value_type* pointer;
	typedef const value_type* const_pointer;
	typedef value_type&       reference;
	typedef const value_type& const_reference;
	typedef std::size_t       size_type;
	typedef std::ptrdiff_t    difference_type;

	template <class U> 
	struct rebind { typedef secure_allocator<U> other; };

	
	secure_allocator() {}
	secure_allocator(const secure_allocator&) {}
	template <class U>  secure_allocator(const secure_allocator<U>&) {}
	~secure_allocator() {}

	pointer address(reference x) const { return &x; }
	const_pointer address(const_reference x) const { 
		return x;
	}

	pointer allocate(size_type n, const_pointer = 0) {
		gpointer p = gcr_secure_memory_alloc(n * sizeof(T));

		if (!p)
			throw std::bad_alloc();
		return static_cast<pointer>(p);
	}

	void deallocate(pointer p, size_type) { 
		gcr_secure_memory_free(p);
	}
	
	size_type max_size() const { 
		return static_cast<size_type>(-1) / sizeof(T);
	}
	
	void construct(pointer p, const value_type& x) { 
		new(p) value_type(x); 
	}
	
	void destroy(pointer p) { p->~value_type(); }
	
private:
	void operator=(const secure_allocator&);
};


template<> class secure_allocator<void>
{
  typedef void        value_type;
  typedef void*       pointer;
  typedef const void* const_pointer;

  template <class U> 
  struct rebind { typedef secure_allocator<U> other; };
};


template <class T>
inline bool operator==(const secure_allocator<T>&, 
                       const secure_allocator<T>&) {
  return true;
}

template <class T>
inline bool operator!=(const secure_allocator<T>&, 
                       const secure_allocator<T>&) {
  return false;
}

typedef std::basic_string< char, std::char_traits<char>, secure_allocator<char> > secure_string;

#endif
